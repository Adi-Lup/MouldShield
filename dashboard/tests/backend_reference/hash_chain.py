# hash_chain.py - makes the readings tamper-evident (T12)
#
# Every reading gets a SHA-256 hash. The hash is calculated from the reading itself
# AND the hash of the reading before it, so all readings are linked in a chain:
#
#   reading 1: prev_hash = 000...000           hash_1 = SHA256(000...000 | reading 1)
#   reading 2: prev_hash = hash_1              hash_2 = SHA256(hash_1 | reading 2)
#   reading 3: prev_hash = hash_2              hash_3 = SHA256(hash_2 | reading 3)
#
# If someone changes an old reading in the database, its hash no longer matches,
# so verify_chain() finds the first reading that was changed.
#
# Limitation: this is tamper-EVIDENT, not tamper-proof. Someone with full access to the
# database could change a reading and calculate all the hashes after it again.

import hashlib

# The first reading has no reading before it, so it is linked to 64 zeros
GENESIS_HASH = "0" * 64


def reading_text(device_id, timestamp, temperature_c, humidity_pct):
    # Builds the text that is hashed. It must be built exactly the same way when the
    # reading is saved and when it is checked, or the hashes will not match.
    # repr(float(...)) always writes the same number in the same way (64.2 -> "64.2"),
    # and SQLite gives back exactly the same number we saved.
    return "|".join([
        str(device_id),
        str(timestamp),
        repr(float(temperature_c)),
        repr(float(humidity_pct)),
    ])


def calculate_hash(prev_hash, device_id, timestamp, temperature_c, humidity_pct):
    # SHA-256 of the previous hash and the reading, as 64 hexadecimal characters
    text = prev_hash + "|" + reading_text(device_id, timestamp, temperature_c, humidity_pct)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_chain(rows):
    # rows: every reading in the order it was saved, as
    # (id, device_id, timestamp, temperature_c, humidity_pct, prev_hash, hash)
    # Returns "OK", or "Tampered" with the id of the first reading that does not match.
    expected_prev = GENESIS_HASH
    previous_id = None

    for checked, row in enumerate(rows):
        row_id, device_id, timestamp, temp, hum, prev_hash, saved_hash = row

        # 1. Is this reading linked to the one before it?
        # If not, the chain is broken between the two: either the reading before it
        # was changed (and its hash calculated again), or this link was changed.
        if prev_hash != expected_prev:
            if previous_id is None:
                reason = "the first reading is not linked to the start of the chain"
            else:
                reason = "chain broken between reading %s and reading %s" % (previous_id, row_id)
            return {"status": "Tampered", "first_bad_id": row_id,
                    "reason": reason, "checked": checked}

        # 2. Does the saved hash still match the reading?
        if saved_hash != calculate_hash(prev_hash, device_id, timestamp, temp, hum):
            return {"status": "Tampered", "first_bad_id": row_id,
                    "reason": "reading changed after it was saved",
                    "checked": checked}

        expected_prev = saved_hash
        previous_id = row_id

    return {"status": "OK", "checked": len(rows)}
