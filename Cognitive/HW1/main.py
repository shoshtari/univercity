import csv
import os
import random
from typing import Sequence

from PIL import Image as PILImage
from psychopy import core, event, visual


def get_probs() -> list[float]:
    probs = [0.4, 0.5, 0.6, 0.7]
    random.shuffle(probs)
    return probs


margin = 0.08
window_width = 900
window_height = 550
card_width = 0.30
card_height = 0.50

win = visual.Window(
    size=[window_width, window_height], color="black", units="height", fullscr=False
)


def _close_win():
    win.close()
    core.quit()


win.winHandle.push_handlers(on_close=_close_win)  # type: ignore


def _wait_for_space():
    while True:
        keys = event.getKeys()
        if "space" in keys:
            return
        core.wait(0.01)


card_positions = [-(margin * 1.5 + card_width * 1.5)]
for i in range(3):
    card_positions.append(card_positions[i] + card_width + margin)

img_size = 0.8 * card_width
treasure_img = visual.ImageStim(
    win=win, image=PILImage.open("pics/treasure.png"), pos=(0, -0.15), size=img_size
)
cross_img = visual.ImageStim(
    win=win, image=PILImage.open("pics/cross.png"), pos=(0, -0.15), size=img_size
)


def show_manual():
    text = (
        "At each block, you should select a card and you either win or lose. each card has a different win probabilty ranging from 0.4 to 0.7.\n"
        "first you must choose a card by pressing a, d, g or j keys, then you will say how sure you are for choosing that card by pressing keys from 1 to 5 and then you see either you win or lose.\n"
        "in the first block, there are 15 rounds. in second block there will be 30 rounds and in final one you must do 45 rounds.\n\n\n"
        "Press space to continue."
    )
    text = visual.TextStim(
        win=win,
        text=text,
        pos=(0, 0),
        color="white",
        height=0.04,
    )
    text.draw()
    win.flip()
    _wait_for_space()


def show_choice_screen(
    probs: Sequence[float], total_trials: int, block_num: int, results_dir: str, all_results: list
):
    card_keys = ("a", "d", "g", "j")
    cards = []
    card_texts = []
    for i in range(4):
        cards.append(
            visual.Rect(  # type: ignore
                win=win,
                width=card_width,
                height=card_height,
                fillColor="gray",
                lineColor="white",
                pos=(card_positions[i], 0.03),
                name=i,
            )
        )
        card_texts.append(
            visual.TextStim(
                win=win,
                text=f"Press {card_keys[i].upper()} to select",
                pos=(card_positions[i], 0.33),
                color="white",
                height=0.04,
            )
        )

    instr_text = visual.TextStim(
        win=win,
        text="Select a card by pressing A, D, G, or J.\nTry to get as many wins as possible!",
        pos=(0, 0.6),
        color="white",
        height=0.04,
    )

    trial_counter = visual.TextStim(
        win=win, text="", pos=(-0.7, 0.47), color="white", height=0.035
    )

    outcome_text = visual.TextStim(
        win=win, text="", pos=(0, -0.32), color="white", height=0.06
    )

    wins = 0
    results = []

    for trial in range(total_trials):
        trial_counter.text = f"Trial {trial + 1} of {total_trials}"

        chosen_card = None
        choice_rt = None
        choice_clock = core.Clock()

        while chosen_card is None:
            pressed_keys = event.getKeys()
            if "escape" in pressed_keys:
                win.close()
                core.quit()

            for card in cards:
                card.lineColor = "white"
                card.draw()
            for card_text in card_texts:
                card_text.draw()
            instr_text.draw()
            trial_counter.draw()

            win.flip()

            for key in card_keys:
                if key in pressed_keys:
                    chosen_card = card_keys.index(key)
                    choice_rt = choice_clock.getTime()
                    cards[chosen_card].lineColor = "purple"
                    break

        win_prob = probs[chosen_card]
        if random.random() < win_prob:
            outcome = "win"
            wins += 1
        else:
            outcome = "lose"

        selected_card = cards[chosen_card]

        confidence_text = visual.TextStim(
            win=win,
            text="How sure are you?\nPress a key from 1 to 5",
            pos=(0, 0.4),
            color="white",
            height=0.05,
        )

        confidence = None
        confidence_rt = None
        conf_clock = core.Clock()

        while confidence is None:
            pressed_keys = event.getKeys()
            if "escape" in pressed_keys:
                win.close()
                core.quit()

            selected_card.draw()
            instr_text.draw()
            trial_counter.draw()
            confidence_text.draw()
            win.flip()

            for key in map(str, range(1, 6)):
                if key in pressed_keys:
                    confidence = int(key)
                    confidence_rt = conf_clock.getTime()
                    break

        if outcome == "win":
            result_img = treasure_img
        else:
            result_img = cross_img
        result_img.pos = (card_positions[chosen_card], -(card_height / 2 + 0.12))

        result_clock = core.Clock()
        while result_clock.getTime() < 1.0:
            if "escape" in event.getKeys():
                win.close()
                core.quit()

            selected_card.draw()
            instr_text.draw()
            trial_counter.draw()
            outcome_text.draw()
            result_img.draw()
            win.flip()

            core.wait(0.01)

        if trial != total_trials - 1:
            black_text = visual.TextStim(
                win=win,
                text="Press space to go to next round",
                pos=(0, 0),
                color="white",
                height=0.05,
            )

            while True:
                pressed_keys = event.getKeys()
                if "escape" in pressed_keys:
                    win.close()
                    core.quit()
                if "space" in pressed_keys:
                    break

                win.flip()
                black_text.draw()
                core.wait(0.01)

        results.append(
            {
                "block": block_num,
                "trial": trial + 1,
                "choice": chosen_card,
                "outcome": outcome,
                "choice_rt": choice_rt,
                "confidence_level": confidence,
                "confidence_rt": confidence_rt,
                "card_probs": str(probs),
            }
        )

    win.flip()
    end_text = visual.TextStim(
        win=win,
        text=f"Block {block_num} Completed!\n\nTotal Score: {wins} Wins / {total_trials} Trials\n\nPress any key to continue.",
        color="white",
        height=0.05,
    )

    end_text.draw()
    win.flip()

    event.waitKeys()
    
    # Add block results to the master results list
    all_results.extend(results)


def get_next_filename(results_dir: str) -> str:
    """Find the next available subject filename (subject1.csv, subject2.csv, etc.)"""
    existing_files = [f for f in os.listdir(results_dir) if f.startswith("subject") and f.endswith(".csv")]
    
    if not existing_files:
        return "subject1.csv"
    
    # Extract numbers from existing subject files
    numbers = []
    for filename in existing_files:
        try:
            # Extract number between "subject" and ".csv"
            num_str = filename[7:-4]  # Remove "subject" and ".csv"
            if num_str.isdigit():
                numbers.append(int(num_str))
        except:
            continue
    
    if not numbers:
        return "subject1.csv"
    
    next_num = max(numbers) + 1
    return f"subject{next_num}.csv"


def save_all_results(results_dir: str, all_results: list):
    """Save all results to a single incremental CSV file"""
    if not all_results:
        return
    
    filename = get_next_filename(results_dir)
    filepath = os.path.join(results_dir, filename)
    
    fieldnames = [
        "block",
        "trial",
        "choice",
        "outcome",
        "choice_rt",
        "confidence_level",
        "confidence_rt",
        "card_probs",
    ]
    
    with open(filepath, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Results saved to {filepath}")


if __name__ == "__main__":
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize master results list
    all_results = []

    show_manual()
    show_choice_screen(get_probs(), 15, 1, results_dir, all_results)
    show_choice_screen(get_probs(), 30, 2, results_dir, all_results)
    show_choice_screen(get_probs(), 45, 3, results_dir, all_results)
    
    # Save all results to a single incremental file
    save_all_results(results_dir, all_results)
    
    win.close()
    core.quit()
