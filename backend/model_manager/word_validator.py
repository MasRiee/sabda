"""
word_validator.py — Cocokkan hasil prediksi model dengan kata target yang
sedang ditampilkan ke pengguna.
"""

import config


def validate(predicted_word: str, target_word: str, confidence: float) -> dict:
    """
    Returns:
        {
            "correct": bool,
            "predicted_word": str,
            "target_word": str,
            "confidence": float,
            "confident_enough": bool,
        }
    """
    confident_enough = confidence >= config.PREDICTION_CONFIDENCE_THRESHOLD
    correct = confident_enough and predicted_word.strip().lower() == target_word.strip().lower()

    return {
        "correct": correct,
        "predicted_word": predicted_word,
        "target_word": target_word,
        "confidence": confidence,
        "confident_enough": confident_enough,
    }
