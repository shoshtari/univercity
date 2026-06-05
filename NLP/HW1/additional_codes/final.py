from pathlib import Path
import random
import re
from collections import Counter, defaultdict
import math

random.seed(1)
WORD_BANK_PATH = Path("hw1_word_bank.txt")
ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
VOWELS = set("aeiou")
EPS = 1e-12
D = 0.75  # Kneser–Ney discount
ERROR_WARN_THRESHOLD = 13
MAX_NGRAM = 5


def decode_signal(secret_word, decoder, max_errors=8, verbose=True, **decoder_args):
    """
    Run the masked-word decoding game and return the number of wrong guesses.

    secret_word: target word in lowercase letters
    decoder: function that proposes the next character
        inputs:
            mask: current known pattern, with "_" for unknown positions
            guessed: set of characters already proposed
            decoder_args: optional extra keyword arguments
    max_errors: maximum number of wrong guesses allowed
    verbose: whether to print step-by-step details
    decoder_args: extra keyword arguments passed to the decoder
    """
    secret_word = secret_word.lower()
    mask = ["_"] * len(secret_word)
    guessed = set()

    if verbose:
        print("Signal decoding started")
        print("Target pattern:", " ".join(mask),
              "| Word length:", len(secret_word))

    errors = 0

    while errors < max_errors:
        if verbose:
            print("Remaining allowed errors:", max_errors - errors)

        guess = decoder(mask, guessed, **decoder_args)

        if verbose:
            print("Proposed character:", guess)

        if guess in guessed:
            if verbose:
                print("This character was already tried.")
            errors += 1
        else:
            guessed.add(guess)

            if guess in secret_word and len(guess) == 1:
                for index, char in enumerate(secret_word):
                    if char == guess:
                        mask[index] = char
                if verbose:
                    print("Correct guess:", " ".join(mask))
            else:
                if len(guess) != 1:
                    print("Please enter exactly one character.")
                if verbose:
                    print("Wrong guess.")
                errors += 1

        if "_" not in mask:
            if verbose:
                print("Decoding completed successfully.")
            return errors

    if verbose:
        print("No attempts left. The original word was:", secret_word)
    return errors


def evaluate_decoder(decoder, evaluation_words, verbose=False):
    """
    Measure the average number of wrong guesses made by a decoder
    over all words in the evaluation set.
    """
    total_errors = 0
    error_by_length = {}
    above_threshold_effect = 0
    for i, word in enumerate(evaluation_words):
        errors = decode_signal(word, decoder, 26, False)
        total_errors += errors
        if len(word) not in error_by_length:
            error_by_length[len(word)] = []
        error_by_length[len(word)].append(errors)
        if verbose and errors > ERROR_WARN_THRESHOLD:
            above_threshold_effect += errors
            print(errors, word)
    if verbose:
        print(
            f"Words with error beyond threshold moved average around {
                above_threshold_effect / float(len(evaluation_words))}"
        )

    return total_errors / float(len(evaluation_words))


with open(WORD_BANK_PATH, "rt") as f:
    data = f.read().split("\n")
    data = [i.strip().lower() for i in data]
    pattern = re.compile("^[a-z]+$")
    data = [i for i in data if pattern.match(i)]
random.shuffle(data)
eval_words = data[:1000]
val_words = data[1000:2000]
train_words = data[2000:]

print("Number of word types in eval =", len(eval_words))
print("Number of word types in val =", len(val_words))
print("Number of word types in train =", len(train_words))


def get_scorer(words):
    ngram_counts = defaultdict(lambda: defaultdict(Counter))

    for word in words:
        PREF = "^" * 4
        padded_word = PREF + word

        for i in range(len(padded_word)):
            for j in range(MAX_NGRAM):
                if i >= len(PREF) - j and i < len(padded_word) - j:
                    prefix = padded_word[i: i + j]
                    char = padded_word[i + j]
                    ngram_counts[j + 1][prefix][char] += 1

    continuation_counts = Counter()
    for _, ctr in ngram_counts[2].items():
        for c in ctr:
            if c in ALPHABET:
                continuation_counts[c] += 1
    total_continuations = sum(continuation_counts.values())

    pos_unigram_counts = defaultdict(lambda: defaultdict(Counter))
    for word in words:
        L = len(word)
        for i, c in enumerate(word):
            pos_unigram_counts[L][i][c] += 1

    def kn_ngram(char, prefix, n):
        nonlocal continuation_counts, ngram_counts

        if n == 1:
            return continuation_counts.get(char, 0) / max(total_continuations, 1)

        ctr = ngram_counts[n][prefix]
        c_xy = ctr.get(char, 0)
        c_x = sum(ctr.values())
        total = len(ctr)
        if c_x == 0:
            return kn_ngram(char, prefix[1:], n - 1)

        return max(c_xy - D, 0) / c_x + (D * total / c_x) * kn_ngram(
            char, prefix[1:], n - 1
        )


    def vc_penalty(char, left, right=None):
        is_vowel = char in VOWELS
        penalty = 0.0
        for ctx in (left, right):
            if ctx and ctx != "_" and ctx != "^":
                if (ctx in VOWELS) == is_vowel:
                    penalty -= 1.0
        return penalty


    def position_prob(char, L, pos, k=0.25):
        ctr = pos_unigram_counts[L][pos]
        total = sum(ctr.values())
        return (ctr.get(char, 0) + k) / (total + k * len(ALPHABET))

    def inner(mask, guessed):
        padded = ["^", "^", "^", "^"] + list(mask)
        L = len(mask)
        scores = Counter()

        # Position weight grows late-game
        alpha = 0.5 * (1 - mask.count("_") / L)

        for c in ALPHABET:
            if c in guessed:
                continue

            log_score = 0.0
            valid = 0

            def get_p(padded, c, ind):
                for i in range(5, 0, -1):
                    pref = "".join(padded[ind - i + 1: ind])
                    if "_" not in pref:
                        return kn_ngram(c, pref, i)

            for i in range(4, len(padded)):
                if padded[i] == "_":
                    p_lm = get_p(padded, c, i)

                    pos = i - 4
                    if L in pos_unigram_counts and pos in pos_unigram_counts[L]:
                        p_pos = position_prob(c, L, pos)
                    else:
                        p_pos = 1.0 / len(ALPHABET)

                    # Vowel-Consonant alternation penalty
                    left = padded[i - 1]
                    right = padded[i + 1] if i + 1 < len(padded) else None
                    vc_adj = 0
                    if len(mask) > 0:
                        vc_adj = vc_penalty(c, left, right)

                    log_score += (
                        math.log(max(p_lm, EPS))
                        + alpha * math.log(max(p_pos, EPS))
                        + vc_adj
                    )
                    valid += 1

            if valid > 0:
                scores[c] = log_score

        return scores


    return inner

scorer1 = get_scorer(train_words)
scorer2 = get_scorer(i[::-1] for i in train_words)
def final_decoder(mask, guessed):
    s1 = scorer1(mask, guessed)
    s2 = scorer2(list(reversed(mask)), guessed)
    s = Counter()

    for k, v in s1.items():
        s[k] += v * 0.5
    for k, v in s2.items():
        s[k] += v * 0.5
    return s.most_common(1)[0][0]

if __name__ == "__main__":
    print("###################################")
    result = evaluate_decoder(
        final_decoder, val_words, verbose=not True
    )
    print("Evaluating 5-gram KN + position + vowel/consonant penalty")
    print("Average number of incorrect guesses:", result)
