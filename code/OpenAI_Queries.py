from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils, translator
import os

df = utils.initialize(engine='davinci')

@st.cache(suppress_st_warning=True)
def get_languages():
    return translator.get_available_languages()

try:

    default_prompt = "Please use only the information provided in the text above to answer questions as a customer service."\
    "\n用客服人员的身份,要求使用礼貌用语,有称呼,称呼需换行。"\
    "\n以列表形式呈现,总结所有和提问相关的信息,列出重要的前10点,每一点需要详细阐述,回答更加有亲和力,重新组织语言进行回答,语气不要生硬。"\
    "\n如果是比较的问题,需要给出优劣势分析。"\
    "\nQuestion: _QUESTION_"\
    "\nAnswer:"
    default_question = "" 
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = os.getenv("QUESTION_PROMPT", default_prompt).replace(r'\n', '\n')
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }    
    if 'limit_response' not in st.session_state:
        st.session_state['limit_response'] = True
    if 'full_prompt' not in st.session_state:
        st.session_state['full_prompt'] = ""

    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    # Get available languages for translation
    available_languages = get_languages()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.image(os.path.join('images','ms.png'))

    col1, col2 = st.columns([8,2])
    with col2:
        with st.expander("Settings"):
            model = os.environ['OPENAI_ENGINES'].split(',')[0]
            st.text_area("Prompt",height=100, key='prompt')
            st.tokens_response = st.slider("Tokens response length", 100, int(os.getenv("TOKEN_MAX","2000")), int(os.getenv("TOKEN_DEFAULT","1600")))
            st.temperature = st.slider("Temperature", 0.0, 1.0, float(os.getenv("DEFAULT_TEMPERATURE","0.8")))
            st.selectbox("Language", [None] + list(available_languages.keys()), key='translation_language')
    with col1:
        question = st.text_input("OpenAI Semantic Answer", default_question)
        if question != '':
            if question != st.session_state['question']:
                st.session_state['question'] = question
                st.session_state['full_prompt'], st.session_state['response'] = utils.get_semantic_answer(df, question, st.session_state['prompt'] ,model=model, engine='davinci', limit_response=st.session_state['limit_response'], tokens_response=st.tokens_response, temperature=st.temperature)
                st.write(f"Q: {question}")  
                st.write(st.session_state['response']['choices'][0]['text'])
                with st.expander("Question and Answer Context"):
                    st.text(st.session_state['full_prompt'].replace('$', '\$')) 
            else:
                st.write(f"Q: {st.session_state['question']}")  
                st.write(f"{st.session_state['response']['choices'][0]['text']}")
                with st.expander("Question and Answer Context"):
                    st.text(st.session_state['full_prompt'].encode().decode())

    if st.session_state['translation_language'] is not None:
        st.write(f"Translation to other languages, 翻译成其他语言, النص باللغة العربية")
        st.write(f"{translator.translate(st.session_state['response']['choices'][0]['text'], available_languages[st.session_state['translation_language']])}")		
		
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
except:
    st.error(os.getenv("DEFAULT_ERROR", "network connection timeout, please try again later."))