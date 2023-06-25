from djl_python import Input, Output
from djl_python.streaming_utils import StreamingUtils
import os
import deepspeed
import torch
import logging
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, AutoModel
from torch import autocast

model = None
tokenizer = None


def get_model(properties):
    model_name = properties["model_id"]
    tensor_parallel_degree = properties["tensor_parallel_degree"]
    # max_tokens = int(properties.get("max_tokens", "1024"))
    # dtype = torch.float16
    # model = LlamaForCausalLM.from_pretrained(model_name, low_cpu_mem_usage=True, torch_dtype=dtype, device_map='auto')
    # tokenizer = LlamaTokenizer.from_pretrained(model_name)
    # tokenizer.pad_token = tokenizer.eos_token
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    # model = AutoModel.from_pretrained(model_name, trust_remote_code=True, torch_dtype=torch.float16, device_map='auto')
    model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()
    
    # tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    tokenizer.padding_side = 'left'

    return model, tokenizer


def inference(inputs):
    try:
        input_map = inputs.get_as_json()
        data = input_map.pop("inputs", input_map)
        history = input_map.pop("history", [])
        parameters = input_map.pop("parameters", {})
        outputs = Output()
        
        with torch.no_grad():
            response, history = model.chat(tokenizer, data, history,**parameters)
        
        outputs.add_as_json({"response": response, "history":history})
        return outputs
    
    except Exception as e:
        logging.exception("Huggingface inference failed")
        # error handling
        outputs = Output().error(str(e))



def handle(inputs: Input) -> None:
    global model, tokenizer
    if not model:
        model, tokenizer = get_model(inputs.get_properties())

    if inputs.is_empty():
        # Model server makes an empty call to warmup the model on startup
        return None

    return inference(inputs)