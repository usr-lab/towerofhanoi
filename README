#Tower of Hanoi 


##Requirements
The project runs on python 2.7 and you will have to install naoqi, opencv, and numpy for it to work.

##Installation
To run this program, you have to install the animations found in the folder _Animations_ (a Choreograph project) and store the updated posture library on NAO. You can find information how to install the custom animations here: [Custom Animations on NAO](https://sebastianwallkoetter.wordpress.com/2019/05/19/custom-animations-during-speech/). You can find information on how to install custom poses here: [Custom Poses on NAO](https://sebastianwallkoetter.wordpress.com/2019/04/05/the-hidden-potential-of-nao-and-pepper-custom-robot-postures-in-naoqi-v2-4/)

After installing the components on NAO, you will need to configure the CV pipeline. This is done via

    configure.py <robot_ip>

At first, you will be presented with a window where you select the color to threshold as well as the threshold parameters. This will happen 5 times, once for each disk color. Then, you will be shown a window where you draw a bounding box around each pole. This will generate a new version of the file `hanoi_config.yaml`. The configuration is quite raw, if you have trouble feel free to submit an issue on this GitHub, and we can see how things can be improved.

After this step, you can start the module via

    play_game.py <condition> <robot_ip>

The two conditions currently in the repository are:

    play_game.py social <robot_ip>
    play_game.py non-social <robot_ip>

If you have any questions or encounter any trouble, feel free to create an issue on this GitHub.

