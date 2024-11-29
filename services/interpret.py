import json
from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Literal, Callable
from services.openai import client

class ParameterProperty(BaseModel):
    type: str
    description: str
    name: str


class Parameters(BaseModel):
    type: Literal["object"]
    properties: Dict[str, ParameterProperty]
    required: List[str]
    additionalProperties: bool


class FunctionDetails(BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(BaseModel):
    type: Literal["function"]
    function: FunctionDetails


class Tools(RootModel):
    root: List[Tool]

    def __init__(
        self,
        tools_data: List[Dict] = None
    ):
        if tools_data is None:
            tools_data = []
        tools = [Tool(**tool_data) for tool_data in tools_data]
        super().__init__(root=tools)

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        parameters_type: Literal["object"],
        properties: List[ParameterProperty],
        required: List[str],
        additional_properties: bool
    ) -> 'Tools':
        parameter_properties = {
            f"param{i+1}": prop for i, prop in enumerate(properties)
        }
        parameters = Parameters(
            type=parameters_type,
            properties=parameter_properties,
            required=required,
            additionalProperties=additional_properties
        )
        function_details = FunctionDetails(
            name=name,
            description=description,
            parameters=parameters
        )
        tool = Tool(
            type="function",
            function=function_details
        )
        return cls(tools_data=[tool.model_dump()])


def interpret_chat(messages: List[str], tools: Tools, functions: Dict[str, Callable]) -> BaseModel:


    # Pass the validated tools data to OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools.root  # Extract the list of tools from the Pydantic model
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # check if the model wanted to call a function
    if tool_calls:
        # call the function
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model                 

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            function_response = function_to_call(**function_args)
            return function_response
