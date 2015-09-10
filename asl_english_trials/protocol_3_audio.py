import os, errno
import expyriment as e
from audio_io import AudioInput

class PictureNamingWithAudio(object):
    protocol = "protocol-3-audio"
    practice_items = ["gamble", "motorcycle", "rocket", "saw", "skate"]
    trial_items = ["argue", "bite", "break", "camp", "carry", "climb", "comb", "count", "dig", "drink", "eat", "exercise", "fight", "haircut", "hide", "hug", "jump", "kick", "kiss", "knot", "listen", "look", "measure", "music", "open", "pay", "pickup", "pour", "pray", "preach", "protest", "sew", "shoot", "sit", "sleep", "smell", "smoke", "stand", "sweep", "swim", "telephone", "think", "turn", "violin", "vomit", "wash", "win", "write"]

    def __init__(self, out_dir='.'):

        try:
            self.output_dir = out_dir+'/'+self.protocol
            os.makedirs(self.output_dir)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

        e.design.randomize.shuffle_list(self.practice_items)
        e.design.randomize.shuffle_list(self.trial_items)

        self.blocks = [
            self.intro(),
            self.practice(),
            self.intermission(),
            self.trials(),
            self.finish(),
        ]

    def intro(self):
        block = e.design.Block('Picture naming with Audio: Intro')
        trial = e.design.Trial()
        intro = """
        In this task, you will be shown pictures of assorted actions.

        Once you have identified the action in the picture, please name it in English as quickly and accurately as you can.

        First, let's try some practice trials. Press enter to continue.
        """
        trial.add_stimulus(e.stimuli.TextBox(intro, (640, 240), text_justification=0))
        trial.present_callback = present_intro
        block.add_trial(trial)

        return block

    def practice(self):
        block = e.design.Block('Picture naming with audio: Practice')

        for item in self.practice_items:
            trial = e.design.Trial()

            trial.set_factor('item', item)
            trial.present_callback = present_practice

            space_bar = """
            Press enter to view the picture.

            When you are ready, name the action in English.
            """
            trial.add_stimulus(e.stimuli.TextBox(space_bar, (640, 240), text_justification=0))

            trial.add_stimulus(e.stimuli.Picture('stimuli/protocol-3/practice/' + item + '.png'))
            trial.add_stimulus(e.stimuli.TextLine('Press enter when you have named the picture', (0, -280)))

            trial.add_stimulus(e.stimuli.TextLine("For reference, here's the kind of word we're looking for..."))
            trial.add_stimulus(e.stimuli.TextLine(item.capitalize()))
            trial.add_stimulus(e.stimuli.TextLine("...and here's what you recorded. Press enter to continue."))

            block.add_trial(trial)

        return block

    def intermission(self):
        block = e.design.Block('Picture naming: Intermission')

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

    def trials(self):
        block = e.design.Block('Picture naming: Trial')
        for idx, item in enumerate(self.trial_items):

            trial = e.design.Trial()
            trial.present_callback = present_trial
            trial.output_dir = self.output_dir

            action_type = 'p' if idx % 2 else 'np'
            image_file = action_type + '_' + item + '.png'
            trial.set_factor('condition', action_type)
            trial.set_factor('item', item)

            trial.add_stimulus(e.stimuli.Picture('stimuli/protocol-3/trial/' + image_file))
            trial.add_stimulus(e.stimuli.TextLine('Press enter to continue', (0, -280)))
            trial.add_stimulus(e.stimuli.TextLine('Please wait...'))

            block.add_trial(trial, random_position=True)

        return block

    def finish(self):
        block = e.design.Block('Picture naming: Finish')

        trial = e.design.Trial()
        intermission = """
        Congratulations, you've made it through!

        Thanks for participating. Press the "up" arrow to end the experiment.
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

    audio = AudioInput('practice')
    blank_line = e.stimuli.TextLine('')

    trial.stimuli[0].present() # press enter and look
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])
    audio.start()

    trial.stimuli[1].present() # practice image
    blank_line.present()
    trial.stimuli[2].present(clear=False) # press enter to continue
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    audio.stop.set()
    filename = audio.convert(trial.config['--ffmpeg'])
    e.control.start_audiosystem()

    trial.stimuli[3].present() # for reference
    exp.clock.wait(1500)

    trial.stimuli[4].present() # sample english word
    exp.clock.wait(2000)

    e.stimuli.Audio(filename).present()
    trial.stimuli[5].present() # what you recorded
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    e.control.stop_audiosystem()

def present_trial(trial, exp, device):
    e.stimuli.FixCross().present()
    exp.clock.wait(2000)

    blank_line = e.stimuli.TextLine('')

    audio_id = 'subject-'+str(exp.subject)+'-'+trial.get_factor('item')
    audio = AudioInput(audio_id, trial.output_dir)
    audio.start()

    trial.stimuli[0].present() # show image
    blank_line.present() # blank

    trial.stimuli[1].present(clear=False) # press enter to continue
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    trial.stimuli[2].present() # please wait
    audio.stop.set()

    exp.data.add([
        PictureNamingWithAudio.protocol,
        '',
        trial.get_factor('item'),
        trial.get_factor('condition'),
        '',
        '',
        audio.filename
    ])

    audio.stopped.wait()

