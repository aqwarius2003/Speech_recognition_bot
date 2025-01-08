import json
import logging
from dotenv import load_dotenv
from google.cloud import dialogflow
import os

logger = logging.getLogger(__name__)


def read_conversation_script_phrases(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        script_phrases = json.load(f)
    return script_phrases


def create_intent(project_id,
                  display_name,
                  training_phrases_parts,
                  message_texts):
    """
    Создает намерение (intent) в проекте Dialogflow.

    Параметры:
    project_id (str): Идентификатор проекта Google Cloud.
    display_name (str): Отображаемое имя намерения.
    training_phrases_parts (list of str): Список фраз для обучения, которые будут использоваться для распознавания
    намерения.
    message_texts (str): Текст сообщения, который будет отправлен в ответ на распознанное намерение.

    Возвращает:
    google.cloud.dialogflow_v2.types.Intent: Объект намерения, созданный в Dialogflow.
    """

    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
        )
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=[message_texts])
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    return response


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    load_dotenv()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    if not project_id:
        logging.error("GOOGLE_CLOUD_PROJECT_ID is not set.")
        return
    else:
        logging.info(f"Using project ID: {project_id}")

    script_path = "questions.json"
    script = read_conversation_script_phrases(script_path)

    for intent_name, intent_data in script.items():
        create_intent(
            project_id,
            intent_name,
            intent_data["questions"],
            intent_data["answer"])


if __name__ == "__main__":
    main()
