import expyriment as e
from collections import namedtuple
from audio_io import DelayedAudioOutput

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

    def __init__(self):
        e.design.randomize.shuffle_list(self.practice_items)

        self.blocks = [
            self.intro(),
            self.practice(),
            self.intermission(),
            #self.trials(),
            self.finish(),
        ]

    def intro(self):
        block = e.design.Block('Translation recognition: Intro')

        trial = e.design.Trial()
        intro = """
        In this task, you will view a sign in ASL and listen to a word in English.

        When you are ready, please indicate whether the ASL sign and the English word are equivalent translations.

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
        return None

    def finish(self):
        block = e.design.Block('Translation production from video: Finish')

        trial = e.design.Trial()
        intermission = """
        Congratulations, you've made it through this segment of the experiment!

        Feel free to get up, walk around, stretch, get some snacks.

        When you're ready, press enter to continue.
        """
        trial.add_stimulus(e.stimuli.TextBox(intermission, (640, 240), text_justification=0))
        trial.present_callback = present_intro

        block.add_trial(trial)

        return block

def present_intro(trial, exp, device):
    trial.stimuli[0].present()
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

def present_practice(trial, exp, device):

    e.control.start_audiosystem()
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

    trial.stimuli[3].present() # please wait...
    while e.control.get_audiosystem_is_playing():
        pass

    e.control.stop_audiosystem()
