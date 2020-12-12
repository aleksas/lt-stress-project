FROM tensorflow/tensorflow:1.12.0-py3

WORKDIR /notebooks
RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/Cleanup_of_Transformer_translate.ipynb

RUN apt install -qq libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg -q -y

RUN pip -q install --upgrade pip
RUN pip -q install requests llvmlite pyaudio sounddevice librosa

EXPOSE 8888
EXPOSE 6006

