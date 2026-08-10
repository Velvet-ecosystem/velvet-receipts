# SPDX-License-Identifier: GPL-3.0-only

import unittest

from audio_output_receipts import (
    AUDIO_OUTPUT_BOOKED,
    AUDIO_OUTPUT_COMPLETED,
    AUDIO_OUTPUT_FAILED,
    AUDIO_OUTPUT_PREEMPTED,
    AUDIO_OUTPUT_RECEIPT_SCHEMA,
    AUDIO_OUTPUT_RECOVERED,
    AUDIO_OUTPUT_STARTED,
    AudioOutputReceiptError,
    audio_output_receipt_from_envelope,
)
from runtime_receipts import runtime_receipt_from_envelope


FLAGS = {
    "evidence_only": True,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
    "audio_output_only": True,
}


class AudioOutputReceiptTests(unittest.TestCase):
    def envelope(self, event_type, **overrides):
        payload = {
            "schema_version": "1.0",
            "output_event_id": "audio-output-001",
            "request_id": "speech-001",
            "node_id": "velvet-audio-pi3-01",
            "priority": 70,
            "output_channels": [4],
            "expression_id": "response-42",
            "profile_id": "owner_default",
            "model_id": "velvet",
            **FLAGS,
        }
        payload.update(overrides)
        return {
            "event_type": event_type,
            "source_id": "octo.playback.primary",
            "sequence": 1,
            "occurred_at_monotonic_ns": 100,
            "payload": payload,
        }

    def test_records_booking_without_copying_spoken_text(self):
        receipt = audio_output_receipt_from_envelope(self.envelope(AUDIO_OUTPUT_BOOKED))
        self.assertEqual(receipt.decision, "record_booking")
        self.assertEqual(receipt.result, "booked")
        self.assertEqual(receipt.domain, "audio-output")
        self.assertEqual(receipt.context["schema"], AUDIO_OUTPUT_RECEIPT_SCHEMA)
        self.assertTrue(receipt.constraints["spoken_text_not_copied"])
        self.assertTrue(receipt.constraints["receipt_is_evidence_not_authority"])

    def test_records_start_and_completion(self):
        started = audio_output_receipt_from_envelope(
            self.envelope(
                AUDIO_OUTPUT_STARTED,
                source_sample_rate_hz=22050,
                playback_sample_rate_hz=48000,
                source_frames=4410,
            )
        )
        self.assertEqual(started.result, "started")

        completed = audio_output_receipt_from_envelope(
            self.envelope(
                AUDIO_OUTPUT_COMPLETED,
                playback_sample_rate_hz=48000,
                frames_written=9600,
                playback_duration_ms=200.0,
            )
        )
        self.assertEqual(completed.decision, "record_completion")
        self.assertEqual(completed.result, "completed")

    def test_records_preemption_relationship(self):
        receipt = audio_output_receipt_from_envelope(
            self.envelope(
                AUDIO_OUTPUT_PREEMPTED,
                playback_sample_rate_hz=48000,
                frames_written=480,
                playback_duration_ms=10.0,
                preempted_by_request_id="safety-002",
            )
        )
        self.assertEqual(receipt.result, "preempted")
        self.assertEqual(receipt.context["preempted_by_request_id"], "safety-002")

    def test_records_failure_and_recovery(self):
        failed = audio_output_receipt_from_envelope(
            self.envelope(
                AUDIO_OUTPUT_FAILED,
                output_channels=[],
                failure_stage="synthesis",
                error_class="SpeechSynthesisError",
                reason="local voice unavailable",
                recovery_required=True,
            )
        )
        self.assertEqual(failed.decision, "record_failure")
        self.assertEqual(failed.result, "synthesis")

        recovered = audio_output_receipt_from_envelope(
            self.envelope(
                AUDIO_OUTPUT_RECOVERED,
                recovered_from_event_id="audio-output-failed-001",
                recovered_from_stage="synthesis",
            )
        )
        self.assertEqual(recovered.result, "recovered")

    def test_rejects_text_raw_audio_and_authority_fields(self):
        for key, value in (
            ("text", "Mister, hello"),
            ("pcm_bytes", "00ff"),
            ("capability_token", "forbidden"),
            ("authorized_by", "Court"),
        ):
            envelope = self.envelope(AUDIO_OUTPUT_BOOKED, **{key: value})
            with self.assertRaisesRegex(AudioOutputReceiptError, "forbidden"):
                audio_output_receipt_from_envelope(envelope)

    def test_runtime_receipt_gateway_dispatches_audio_output(self):
        receipt = runtime_receipt_from_envelope(self.envelope(AUDIO_OUTPUT_BOOKED))
        self.assertEqual(receipt.policy, "AudioOutputEvidenceContract")
        self.assertEqual(receipt.event, AUDIO_OUTPUT_BOOKED)


if __name__ == "__main__":
    unittest.main()
