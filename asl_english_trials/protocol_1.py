import expyriment as e
import csv
from collections import namedtuple

Stimuli = namedtuple('Stimuli', ['item', 'video', 'audio', 'condition'])

class TranslationRecognition(object):
    protocol = "protocol-1"
    practice_items = [
        Stimuli('saw', 'saw', 'saw', 'practice'),
        Stimuli('rollerskate', 'rollerskate', 'rollerskate', 'practice'),
        Stimuli('rocket', 'rocket', 'research', 'practice'),
        Stimuli('gamble', 'rollerskate', 'soon', 'practice'),
        Stimuli('motorcycle', 'motorcycle', 'motorcycle', 'practice'),
    ]
    trial_items = {
        'list1' : [],
        'list2' : [],
        # 'list3' : [], # list3 is broken
        'list4' : [],
    }

    def __init__(self):
        e.design.randomize.shuffle_list(self.practice_items)
        self.load_trials()

        self.blocks = [
            self.intro(),
            self.practice(),
            self.intermission(),
            self.trial(),
            self.finish(),
        ]

    def load_trials(self):
        for list_name, items in self.trial_items.iteritems():
            with open('stimuli/protocol-1/trial/'+list_name+'.csv') as list_file:
                reader = csv.reader(list_file)
                next(reader, None)
                for row in reader:
                    items.append(Stimuli(row[2], row[4], row[5], row[3]))

            e.design.randomize.shuffle_list(self.trial_items[list_name])

    def intro(self):
        block = e.design.Block('Translation recognition: Intro')

        trial = e.design.Trial()
        intro = """
        In this task, you will view a sign in ASL and listen to a word in English.

        As quickly and accurately as you can, indicate whether the ASL sign and the English word are equivalent translations.

        First, let's try some practice trials. Press enter to continue.
        """
        trial.add_stimulus(e.stimuli.TextBox(intro, (640, 240), text_justification=0))
        trial.present_callback = present_intro

        block.add_trial(trial)

        return block

    def practice(self):
        block = e.design.Block('Translation recognition: Practice')

        for item in self.practice_items:
            trial = e.design.Trial()

            trial.set_factor('item', item.item)
            trial.set_factor('audio', item.audio)
            trial.set_factor('video', item.video)
            trial.present_callback = present_practice

            intro = """
            Press enter to view the ASL sign/English word pair.

            When you are ready, press the "yes" key if the sign and word are equivalent translations, and the "no" key if they are not.
            """
            trial.add_stimulus(e.stimuli.TextBox(intro, (640, 240), text_justification=0))
            trial.add_stimulus(e.stimuli.Audio('stimuli/practice/' + item.audio + '.ogg'))
            trial.add_stimulus(e.stimuli.Video('stimuli/practice/' + item.video + '.mpeg1'))
            trial.add_stimulus(e.stimuli.TextLine("Please wait..."))


            block.add_trial(trial)

        return block

    def intermission(self):
        block = e.design.Block('Translation recognition: Intermission')

        trial = e.design.Trial()
        intermission = """
        Nice job! You should be ready to start the real thing.

        If you are confused, or the instructions are unclear, please talk to Benjamin before you continue.

        When you are ready to start the experiment, press enter.
        """
        trial.add_stimulus(e.stimuli.TextBox(intermission, (640, 240), text_justification=0))
        trial.present_callback = present_intro

        block.add_trial(trial)

        return block

    def trial(self):
        block = e.design.Block('Translation recognition: Trial')

        for list_name, items in self.trial_items.iteritems():
            for item in items:

                video_dir = 'filler' if item.item == item.video else item.condition
                audio_dir = 'filler' if item.item == item.audio else item.condition

                audio_file = 'stimuli/protocol-1/trial/audio/'+audio_dir+'/'+item.audio+'.ogg'
                video_file = 'stimuli/protocol-1/trial/video/'+video_dir+'/'+item.video+'.mpeg1'

                trial = e.design.Trial()

                trial.set_factor('item', item.item)
                trial.set_factor('audio', item.audio)
                trial.set_factor('video', item.video)
                trial.set_factor('condition', item.condition)
                trial.set_factor('list', list_name)

                trial.present_callback = present_trial

                trial.add_stimulus(e.stimuli.Audio(audio_file))
                trial.add_stimulus(e.stimuli.Video(video_file))
                trial.add_stimulus(e.stimuli.TextLine("Please wait..."))


                block.add_trial(trial, random_position=True)

        return block

    def finish(self):
        block = e.design.Block('Translation recognition: Finish')

        trial = e.design.Trial()
        intermission = """
        Congratulations, you've made it through this segment of the experiment!

        Feel free to get up, walk around, stretch, get some snacks.

        When you're ready, press the "up" arrow to continue.
        """
        trial.add_stimulus(e.stimuli.TextBox(intermission, (640, 240), text_colour=(242, 239, 34), text_justification=0))
        trial.present_callback = present_finish

        block.add_trial(trial)

        return block

def present_finish(trial, exp, device):
    trial.stimuli[0].present()
    exp.keyboard.wait([e.misc.constants.K_UP])

def present_intro(trial, exp, device):
    trial.stimuli[0].present()
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

def present_practice(trial, exp, device):

    blank_line = e.stimuli.TextLine('')

    trial.stimuli[0].present() # press enter and watch/listen
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    blank_line.present()
    blank_line.present()
    trial.stimuli[2].present()
    while trial.stimuli[2].is_playing:
        trial.stimuli[2].update()

    e.control.start_audiosystem()
    blank_line.present()
    trial.stimuli[1].present()
    audio_start = exp.clock.stopwatch_time

    key, rt = exp.keyboard.wait([e.misc.constants.K_c, e.misc.constants.K_m])
    rt = exp.clock.stopwatch_time - audio_start

    correct = 'yes' if trial.get_factor('audio') == trial.get_factor('video') else 'no'
    response = 'yes' if key == e.misc.constants.K_c else 'no'

    if correct == response:
        line = 'Good job! You said "'+response+'", and the correct response was "'+correct+'".'
    else:
        line = 'Oops! You said "'+response+'", but the correct response was "'+correct+'".'
    e.stimuli.TextLine(line).present()
    exp.clock.wait(2000)

    while e.control.get_audiosystem_is_playing():
        pass

    e.control.stop_audiosystem()

def present_trial(trial, exp, device):

    # run trials based on the subject id
    # (THIS IS SO CHEATING)
    order = exp.subject % 3 # will be 4 when list3 is fixed
    if not order: order = 4 # will be 4 when list3 is fixed
    if trial.get_factor('list') != 'list'+str(order):
        return

    blank_line = e.stimuli.TextLine('')

    blank_line.present()
    blank_line.present()
    trial.stimuli[1].present()
    while trial.stimuli[1].is_playing:
        trial.stimuli[1].update()

    e.control.start_audiosystem()
    blank_line.present()
    trial.stimuli[0].present()
    audio_start = exp.clock.stopwatch_time

    key, rt = exp.keyboard.wait([e.misc.constants.K_c, e.misc.constants.K_m])
    reaction_time = exp.clock.stopwatch_time - audio_start

    response = 'yes' if key == e.misc.constants.K_c else 'no'

    trial.stimuli[2].present() # please wait...
    exp.clock.wait(1500)

    exp.data.add([
        TranslationRecognition.protocol,
        trial.get_factor('list'),
        trial.get_factor('item'),
        trial.get_factor('condition'),
        '',
        reaction_time,
        response,
    ])

    while e.control.get_audiosystem_is_playing():
        pass
    e.control.stop_audiosystem()
