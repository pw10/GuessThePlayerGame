import pandas as pd
import random
import os
import numpy as np


# Data import and preparation
data = pd.read_csv("data.csv", sep=",", encoding="ISO-8859-1").drop(["Rk", "Matches", "Age", 'Gls.1', 'Ast.1', 'G+A',
                                                                     'G-PK.1', 'G+A-PK', 'xG.1', 'xA.1', 'xG+xA',
                                                                     'npxG.1', 'npxG+xA.1', 'G-PK', 'npxG+xA', 'npxG'],
                                                                    axis=1)

# correcting players
players = [player.split("\\", 1)[1] for player in data.Player]
players = [player.replace("-", " ", 1) for player in players]

# temp = [player for player in players if "-" in player]
# for i in range(len(temp)):
#     print(temp[i], end=' ')
#     print()

# few of them are specific so I found with for loop them and corrected manually
players[players.index('Emile Smith-Rowe')] = 'Emile Smith Rowe'
players[players.index('Georges Kevin-NKoudou')] = 'Georges-Kevin NKoudou'
players[players.index('Alexis Mac-Allister')] = 'Alexis Mac Allister'
players[players.index('Giovani Lo-Celso')] = 'Giovani Lo Celso'
players[players.index('Anwar El-Ghazi')] = 'Anwar El Ghazi'
players[players.index('David de-Gea')] = 'David de Gea'
players[players.index('Jean Philippe-Gbamin')] = 'Jean-Philippe Gbamin'
players[players.index('Virgil van-Dijk')] = 'Virgil van Dijk'
players[players.index('Kevin De-Bruyne')] = 'Kevin De Bruyne'
players[players.index('Johann Berg-Gudmundsson')] = 'Johann Berg Gudmundsson'
players[players.index('Pierre Emerick-Aubameyang')] = 'Pierre-Emerick Aubameyang'
players[players.index('Patrick van-Aanholt')] = 'Patrick van Aanholt'

data.Player = players

# looking for duplicates - few players changed team during winter transfer window
# and data for them was stored in 2 observations, 1 for every team

# print(len(players) == len(set(players)))

# finding indexes of duplicated players
duplicated_inx = [i for i, x in enumerate(players) if players.count(x) > 1]

# print(data.iloc[duplicated_inx])

cols = ['MP', 'Starts', 'Min', '90s', 'Gls', 'Ast', 'PK', 'PKatt', 'CrdY', 'CrdR', 'xG', 'xA']

for i in range(0, int(len(duplicated_inx)), 2):
    k = duplicated_inx[i]
    for x in cols:
        data.loc[k, x] = data.loc[k, x] + data.loc[k + 1, x]
    data.loc[k, 'Squad'] = data.loc[k, 'Squad'] + ", " + data.loc[k + 1, 'Squad']  # squad column
    data.drop(int(k + 1), axis=0, inplace=True)

data.reset_index(inplace=True, drop=True)

for i in range(0, len(data.Pos)):
    if len(data.Pos[i]) > 2:
        data.loc[i, 'Pos'] = data.loc[i, 'Pos'][:2] + ", " + data.loc[i, 'Pos'][2:]

big6 = ['Arsenal', 'Liverpool', 'Leicester', 'Manchester City', 'Manchester Utd', 'Chelsea']

data['Big6'] = np.where(data['Squad'].isin(big6), 'Yes', "No")

cond = [((data['MP'] <= 9) | (data['Min'] <= 342)),
        ((data['Gls'] > 15) | (data['Ast'] > 8) | (data['MP'] >= 38)),
        (~(((data['MP'] <= 9) | (data['Min'] <= 342)) | ((data['Gls'] > 15) | (data['Ast'] > 8) | (data['MP'] >= 38))) &
         (data['Big6'] == 'No')),
        (~(((data['MP'] <= 9) | (data['Min'] <= 342)) | ((data['Gls'] > 15) | (data['Ast'] > 8) | (data['MP'] >= 38))) &
         (data['Big6'] == 'Yes'))]

tiers = [4, 1, 3, 2]

data['level'] = np.select(cond, tiers)


def tips(data_, index_):
    # 1st tip: playing time stats and position
    first_tip = "Playing time stats and position:\n" \
                "Matches played: " + str(data_.loc[index_, 'MP']) + "\n" + \
                "Matches started: " + str(data_.loc[index_, 'Starts']) + "\n" + \
                "Minutes played: " + str(data_.loc[index_, 'Min']) + "\n" + \
                "Minutes per game: " + str(data_.loc[index_, 'Min'] / data_.loc[index_, 'MP']) + "\n" \
                                                                                                 "Position: " + str(
        data_.loc[index_, 'Pos'])

    # 2nd tip: goals and penalties
    second_tip = "Goals and penalties stats:\n" \
                 "Goals scored: " + str(data_.loc[index_, 'Gls']) + "\n" \
                                                                    "Expected Goals: " + str(
        data_.loc[index_, 'xG']) + "\n" \
                                   "Penalties (attempted/scored): " + str(data_.loc[index_, 'PKatt']) + "/" + str(
        data_.loc[index_, 'PK'])

    # 3rd tip: assists and cards
    third_tip = "Assists and cards stats:\n" \
                "Assists: " + str(data_.loc[index_, 'Ast']) + "\n" \
                                                              "Expected assists: " + str(data_.loc[index_, 'xA']) + "\n" \
                                                                                                                    "Yellow cards: " + str(
        data_.loc[index_, 'CrdY']) + "\n" \
                                     "Red cards: " + str(data_.loc[index_, 'CrdR'])

    # 4th tip: nationality and position
    fourth_tip = "Nationality: " + str(data_.loc[index_, 'Nation']) + "\n" \
                                                                      "Year of birth: " + str(data_.loc[index_, 'Born'])

    # 5th, last tip: team name and birth date
    last_tip = "Team name: " + data_.loc[index_, 'Squad']

    return [first_tip, second_tip, third_tip, fourth_tip, last_tip]


def play_the_game(data_, first=True):
    if first:
        print("Hello! Welcome in the game for Premier League fans!\n"
              "Your task is to guess which Premier League player is described with our tips!\n"
              "In the data set we have 515 players that were reported for PL competition in 2019/2020 season.\n"
              "You are going to see 5 tips that include following stats from this season:\n"
              "1st tip: playing time stats\n"
              "2nd tip: goals and penalties stats\n"
              "3rd tip: assists and cards stats\n"
              "4th tip: nationality and position\n"
              "5th tip: team and year of birth\n"
              "Based on the tips you have to guess the player. Remember - it may be someone really outstanding in that "
              "period like Mo Salah, but also someone who played poorly or didn't play much, so level of difficulty "
              "may be very different!\n"
              "\n Let's start! (Click enter to start)")
        input()
        os.system('cls')


    print("Choose level of difficulty - 1 / 2 / 3 / 4 (from the easiest to the hardest:")
    diff_rate = input()

    try:
        diff_rate = int(diff_rate)
    except:
        print("Inappropriate level - it has to be an integer 1/2/3/4!\n"
              "We set level = 1. If you want harder task remember to correctly insert level next time!")
        diff_rate = 1

    if diff_rate not in [1, 2, 3, 4]:
        print("Inappropriate level - it has to be an integer 1/2/3/4!\n"
              "We set level = 1. If you want harder task remember to correctly insert level next time!")
        diff_rate = 1

    os.system('cls')
    indices = data_.index[data_.level == diff_rate]
    inx = random.choice(indices)
    # global drawn_inx
    # while inx in drawn_inx:
    #     inx = randint(0, int(data_.shape[0] - 1))
    # drawn_inx.append(inx)
    player_to_guess = data_.Player[inx]

    tip_list = tips(data_, inx)

    print("Let's start! First tip:")
    print(tip_list[0])

    print("If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
    temp = input()

    while temp not in ['0', '1']:
        print("Inappropriate sign!\n"
              "If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
        temp = input()

    # after 1st decision
    if temp == '1':
        print("Write first and last name of a player and click enter:\n")
        guess = input()
        if guess == player_to_guess:
            print("You won!")
            return
        else:
            print("You lost :(\n"
                  "The answer is: " + str(player_to_guess))
            return
    else:
        print("So here is the second tip!")
        print(tip_list[1])

    print("If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
    temp = input()

    while temp not in ['0', '1']:
        print("Inappropriate sign!\n"
              "If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
        temp = input()

    # after 2nd decision
    if temp == '1':
        print("Write first and last name of a player and click enter:\n")
        guess = input()
        if guess == player_to_guess:
            print("You won!")
            return
        else:
            print("You lost :(\n"
                  "The answer is: " + str(player_to_guess))
            return
    else:
        print("So here is the third tip!")
        print(tip_list[2])

    print("If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
    temp = input()

    while temp not in ['0', '1']:
        print("Inappropriate sign!\n"
              "If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
        temp = input()

    # after 3rd decision
    if temp == '1':
        print("Write first and last name of a player and click enter:\n")
        guess = input()
        if guess == player_to_guess:
            print("You won!")
            return
        else:
            print("You lost :(\n"
                  "The answer is: " + str(player_to_guess))
            return
    else:
        print("So here is the forth tip!")
        print(tip_list[3])

    print("If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
    temp = input()

    while temp not in ['0', '1']:
        print("Inappropriate sign!\n"
              "If you want to guess write 1 and click enter. If you want another hint - write 0 and click enter!")
        temp = input()

    # after 4th decision
    if temp == '1':
        print("Write first and last name of a player and click enter:\n")
        guess = input()
        if guess == player_to_guess:
            print("You won!")
            return
        else:
            print("You lost :(\n"
                  "The answer is: " + str(player_to_guess))
            return
    else:
        print("So here is the fifth (last!) tip!")
        print(tip_list[4])

    print("All tips have been shown - time to check your guess!")
    print("Write first and last name of a player and click enter:")
    guess = input()

    if guess == player_to_guess:
        print("You won!")
        return
    else:
        print("You lost :(\n"
              "The answer is: " + str(player_to_guess))
        return


play_next = True
first_game = True

while play_next:
    play_the_game(data, first_game)
    print("Do you want to play once again?\n"
          "If you do then insert any sign(s) and click enter.\n"
          "If you want to end the game just click enter!")
    decision = input()
    if decision != '':
        first_game = False
    else:
        play_next = False

