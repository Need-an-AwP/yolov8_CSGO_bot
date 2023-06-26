from ultralytics import YOLO
import multiprocessing as mp

if __name__ == '__main__':
    mp.freeze_support()
    # Load a model
    model = YOLO('yolov8m.pt')  # load a pretrained model (recommended for training)

    # Train the model
    model.train(data=r'D:\yolov8_CSGO_bot\BOT\train\data.yaml', epochs=1000, imgsz=1056, batch=4)
