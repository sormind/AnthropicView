import cv2
import numpy as np
import pyautogui
import json
import time
import anthropic
import base64

API_KEY = 'ANTHROPIC_API_KEY'
actions_log = 'actions.log'

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def recognize_actions(screenshot):
    _, img_encoded = cv2.imencode('.jpg', screenshot)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    
    client = anthropic.Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "Recognize actions in the image above."
                    }
                ]
            }
        ]
    )
    
    try:
        actions = json.loads(message.content)
    except json.JSONDecodeError:
        actions = {'actions': [{'type': 'text', 'text': message.content}]}
    
    return actions

def annotate_actions(screenshot, actions):
    for action in actions.get('actions', []):
        if action['type'] == 'click':
            x, y = action['coordinates']
            screenshot = cv2.circle(screenshot, (x, y), 20, (255, 0, 0), 2)
    return screenshot

def log_action(action):
    with open(actions_log, 'a') as f:
        f.write(json.dumps(action) + "\n")

def recognize_and_annotate():
    screenshot = capture_screenshot()
    actions = recognize_actions(screenshot)
    screenshot = annotate_actions(screenshot, actions)
    for action in actions.get('actions', []):
        log_action(action)
    return screenshot

def replicate_actions():
    with open(actions_log, 'r') as f:
        actions = f.readlines()

    for action in actions:
        action = json.loads(action)
        if action['type'] == 'click':
            x, y = action['coordinates']
            pyautogui.click(x, y)
            time.sleep(1.0)  # Adjusted delay

def main():
    while True:
        screenshot = recognize_and_annotate()
        cv2.imshow("Screen", screenshot)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    # Uncomment the following line to replicate actions
    replicate_actions()
