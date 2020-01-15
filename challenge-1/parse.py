#!/usr/bin/env python
import csv
import enum
import sys


class N7110KeypadKeys(enum.Enum):
    N7110_KEYPAD_ZERO = 0
    N7110_KEYPAD_ONE = 1
    N7110_KEYPAD_TWO = 2
    N7110_KEYPAD_THREE = 3
    N7110_KEYPAD_FOUR = 4
    N7110_KEYPAD_FIVE = 5
    N7110_KEYPAD_SIX = 6
    N7110_KEYPAD_SEVEN = 7
    N7110_KEYPAD_EIGHT = 8
    N7110_KEYPAD_NINE = 9
    N7110_KEYPAD_STAR = 10
    N7110_KEYPAD_HASH = 11
    N7110_KEYPAD_MENU_LEFT = 100
    N7110_KEYPAD_MENU_RIGHT = 101
    N7110_KEYPAD_MENU_UP = 102
    N7110_KEYPAD_MENU_DOWN = 103
    N7110_KEYPAD_CALL_ACCEPT = 104
    N7110_KEYPAD_CALL_REJECT = 105


class N7110ImeMethods(enum.Enum):
    N7110_IME_T9 = 0
    N7110_IME_T9_CAPS = 1
    N7110_IME_ABC = 2
    N7110_IME_ABC_CAPS = 3


N7110_KEYPAD_ZERO_ABC_CHARS  = " 0"
N7110_KEYPAD_ONE_ABC_CHARS   = ".,'?!\"1-()@/:"
N7110_KEYPAD_TWO_ABC_CHARS   = "abc2"
N7110_KEYPAD_THREE_ABC_CHARS = "def3"
N7110_KEYPAD_FOUR_ABC_CHARS  = "ghi4"
N7110_KEYPAD_FIVE_ABC_CHARS  = "jkl5"
N7110_KEYPAD_SIX_ABC_CHARS   = "mno6"
N7110_KEYPAD_SEVEN_ABC_CHARS = "pqrs7"
N7110_KEYPAD_EIGHT_ABC_CHARS = "tuv8"
N7110_KEYPAD_NINE_ABC_CHARS  = "wxyz9"
N7110_KEYPAD_STAR_ABC_CHARS  = "@/:_;+&%*[]{}"
N7110_KEYPAD_HASH_CHARS      = N7110ImeMethods


KEYPRESS = {
    N7110KeypadKeys.N7110_KEYPAD_ZERO.value: N7110_KEYPAD_ZERO_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_ONE.value: N7110_KEYPAD_ONE_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_TWO.value: N7110_KEYPAD_TWO_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_THREE.value: N7110_KEYPAD_THREE_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_FOUR.value: N7110_KEYPAD_FOUR_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_FIVE.value: N7110_KEYPAD_FIVE_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_SIX.value: N7110_KEYPAD_SIX_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_SEVEN.value: N7110_KEYPAD_SEVEN_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_EIGHT.value: N7110_KEYPAD_EIGHT_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_STAR.value: N7110_KEYPAD_STAR_ABC_CHARS,
    N7110KeypadKeys.N7110_KEYPAD_NINE.value: N7110_KEYPAD_NINE_ABC_CHARS,
}


if __name__ == "__main__":
    filename = sys.argv[1]

    with open(filename, 'r') as handler:
        reader = csv.reader(handler)

        prev_time = 0       # timestamp from the previous line
        prev_code = None    # keypad value from the previous line
        code_index = 0      # number of times the previous keypad value has been pressed
        message = []        # characters that make up the final message
        cursor_index = 0    # index of the cursor

        try:
            for next_time, next_code in reader:
                next_time = int(next_time)
                next_code = int(next_code)
                diff_time = next_time - prev_time

                if prev_code is None:
                    pass

                elif next_code != prev_code or diff_time > 1000:
                    chars = KEYPRESS.get(prev_code)
                    if chars:
                        message.insert(cursor_index, chars[code_index % len(chars)])
                        cursor_index += 1
                    code_index = 0

                elif next_code == prev_code:
                    code_index += 1

                # menu right appears to be deleting chars
                if prev_code == 101:
                    cursor_index -= 1
                    message.pop(cursor_index)

                # menu up moves the cursor to the left
                if prev_code == 102:
                    cursor_index -= 1

                # menu down moves the cursor to the right
                if prev_code == 103:
                    cursor_index += 1

                prev_time = next_time
                prev_code = next_code

        finally:
            print(''.join(message))
