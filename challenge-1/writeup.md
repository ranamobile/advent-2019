# Challenge

* **Title**: 7110
* **Tags**: keylogger, programming, pwned!
* **Author**: wasamasa

Santa is stranded on the Christmas Islands and is desperately trying to reach his trusty companion via cellphone. We've bugged the device with a primitive keylogger and have been able to decode some of the SMS, but couldn't make much sense of the last one. Can you give us a hand?

Download: f01d32e3f32957cf42f9672e78fcb415c6deac398fdacbd69531a322b08a39c8-7110.tar.gz

# Triage

First things first, let's see what's inside the tarball.

```
$ tar xf f01d32e3f32957cf42f9672e78fcb415c6deac398fdacbd69531a322b08a39c8-7110.tar.gz
$ ls
f01d32e3f32957cf42f9672e78fcb415c6deac398fdacbd69531a322b08a39c8-7110.tar.gz
keys.h
sms1.csv
sms1.txt
sms2.csv
sms2.txt
sms3.csv
sms3.txt
sms4.csv
```

It looks like we have a header file `keys.h` containing what looks like keys and values for an old school phone keypad. This makes sense considering the timestamps in the .txt files are from the year 1999! If you're old enough to remember these amazing phones, you'll immediately recognize the T9 typing pattern. If not, you'll see hints of T9 in the constant names as well.

Given the pairs of txt and csv files, you can infer the CSV files contain the raw keylogger key presses and the corresponding TXT files contain the generated results. All we have to do is write a parser script that will convert the CSV to match the TXT! Then we can generate a TXT for the missing file `sms4.txt`. Just maybe the flag is in there!

# First Iteration

The basics of T9 essentially type letters to the screen by pressing the key containing the character you want the number of times of its index. For example, to type the letter L, you would press the 5 key three times.

To get a duplicate key, you wait one second between entering the character. For example, to type the letters LL, you would press the 5 key three times, wait one second, and then press the the 5 key three more times.

With that in mind, we can start with iterating over the CSV file. If you look up SMS CSV files, you'll see that most formats include a timestamp which could be only the first column given the size of the values. The second column appears to be keypad values that corresponds to the `keys.h` file.

(Note, Python is my goto, and so I converted the `keys.h` into Python enum and dictionary. In the below chunk of code, `KEYPRESS` is a dictionary of the keypad value as the key, and the characters of that keypad as the value. See the full code snippet in the appendix!)

```python
import csv

with open('sms1.csv', 'r') as handler:
    reader = csv.reader(handler)

    prev_time = 0       # timestamp from previous line
    prev_code = None    # keypad value from previous line
    code_index = 0      # number of times keypad value has been pressed
    message = ''        # final SMS message

    for next_time, next_code in reader:
        next_time = int(next_time)
        next_code = int(next_code)
        diff_time = next_time - prev_time

        # this is the first pass, so don't do anything
        if prev_code is None:
            pass

        # ************************* MAGIC HAPPENING *************************
        # a new keypad value was pressed or one second has passed since the
        # last keypress, so convert the keypad value and the number of times
        # it was pressed into a character and append it on the final message
        elif next_code != prev_code or diff_time > 1000:
            chars = KEYPRESS.get(prev_code)
            if chars:
                message += chars
            code_index = 0

        # keypad value was pressed again, so increment the count
        elif next_code == prev_code:
            code_index += 1

        # get ready for next iteration
        prev_time = next_time
        prev_code = next_code
```

When running it on `sms1.csv`, you get a message that matches the `sms.txt` file!

```
original:   rudolf where are you brrr
extracted:  rudolf where are you brrr0m, .l ,p
```

Let's just ignore the trailing characters for now...

# Second Iteration

Unfortunately, when you try to run the same script on `sms2.csv`, the message mostly matches except some extra characters made it into the final message. Weird!

```
original:   its too damn cold here and im out of eggnog lul
extracted:  its fuckingtoo damn cold here and im out of eggnog lul0m.. .l ,p
```

Maybe it's time we pay attention to the menu keypad values as well! If you eyeball the `sms2.csv`, you'll see several keypresses of the `101` code. Since there are characters that appeared in the parsed message but not in the final text, we can infer this could be the delete key.

This isn't too complicated of an operation, so let's add at the end of the loop deleting the last character when we see this code.

```python
        if prev_code == 101:
            message = message[:-1]
```

Voila! This spits out the right message now for both `sms2` and `sms1`!

```
original:   its too damn cold here and im out of eggnog lul
extracted:  its too damn cold here and im out of eggnog lul0m.. .l ,p
```

Let's just keep ignoring the trailing characters...

# Third Iteration

And then again, we see this breaks for `sms3.csv`. Sad...

```
original:   sorry bout my last 2msg but i could really need your help bud :*
extracted:  sorri bout my last 2msg but i could realy need your help budy :*0m, .l ,p
```

You can see there are a couple discrepancies between the original and extracted including the misspelling of `sorri` and `realy`. When eyeballing the `sms3.csv` file, there are two more keypad codes (`102` and `103`) that we've ignored but probably of significance. From the name of these keys in the `keys.h` file, they represent `MENU_UP` and `MENU_DOWN` respectively. Again, making another guess, perhaps they move the cursor to the appropriate location before adding/deleting characters.

We'll need a new variable to track the cursor location, but let's add that to the loop!

```python
    message = []        # characters that make up the final message
    cursor_index = 0    # index of the cursor

    for next_time, next_code in reader:

        ...

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
```

That did it! Amazing!

```
original:   sorry bout my last 2msg but i could really need your help bud :*
extracted:  sorry bout my last 2msg but i could really need your help bud :*0m, .l ,p
```

Let's try it on the last CSV file too!

```
alright pal heres ye flag good luck entering it with those hooves lol its aotw{l3ts_dr1nk_s0m3_eggn0g_y0u_cr4zy_d33r}0m.. .l ,p
```

YES, found the flag! Still don't know what those trailing characters mean, but since they're similar in all messages, it's probably the keypresses for sending the text.

# Appendix - Full Source

```python
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
```
