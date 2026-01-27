"""
Lógica LLM (GPT-4o-mini) -> JSON
Parser de instrucciones usando LLM
"""

import json
import time
from typing import Optional, Dict, Any
from src.common.types import Instruction
from src.common.logger import get_logger

logger = get_logger(__name__)


class InstructionParser:
    """
    Parsea instrucciones de lenguaje natural a formato JSON estructurado
    usando un LLM (GPT-4o-mini)
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Inicializa el parser de instrucciones
        
        Args:
            api_key: API key de OpenAI
            model: Modelo de LLM a usar
            temperature: Temperatura para la generación
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        
        logger.info(f"InstructionParser initialized (model: {model})")
        
        # TODO: Inicializar cliente de OpenAI
        # self.client = openai.Client(api_key=api_key)
    
    def _create_system_prompt(self) -> str:
        """Crea el prompt del sistema para el LLM"""
        return """You are an aviation instruction parser. Convert pilot instructions to JSON format.

Expected JSON format:
{
    "instruction_type": "heading|altitude|speed|flaps|gear|throttle",
    "parameters": {
        "value": <number>,
        "unit": "<unit>"
    }
}

Examples:
- "Turn left heading 270" -> {"instruction_type": "heading", "parameters": {"value": 270, "unit": "degrees"}}
- "Climb and maintain 5000 feet" -> {"instruction_type": "altitude", "parameters": {"value": 5000, "unit": "feet"}}
- "Reduce speed to 180 knots" -> {"instruction_type": "speed", "parameters": {"value": 180, "unit": "knots"}}

Return ONLY valid JSON, no additional text."""
    
    def parse(self, text: str) -> Optional[Instruction]:
        """
        Parsea texto de lenguaje natural a instrucción estructurada
        
        Args:
            text: Texto de la instrucción
            
        Returns:
            Objeto Instruction, o None si hay error
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for parsing")
            return None
        
        logger.info(f"Parsing instruction: '{text}'")
        
        try:
            # TODO: Hacer llamada real al LLM
            # response = self.client.chat.completions.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": self._create_system_prompt()},
            #         {"role": "user", "content": text}
            #     ],
            #     temperature=self.temperature
            # )
            # parsed_json = json.loads(response.choices[0].message.content)
            
            # Placeholder: simulación de respuesta del LLM
            parsed_json = {
                "instruction_type": "heading",
                "parameters": {"value": 270, "unit": "degrees"}
            }
            
            instruction = Instruction(
                instruction_type=parsed_json["instruction_type"],
                parameters=parsed_json["parameters"],
                raw_text=text,
                timestamp=time.time(),
                confidence=0.95
            )
            
            logger.info(f"Successfully parsed instruction: {instruction.instruction_type}")
            return instruction
            
        except Exception as e:
            logger.error(f"Error parsing instruction: {e}")
            return None
    
    def validate_instruction(self, instruction: Instruction) -> bool:
        """
        Valida que una instrucción tenga el formato correcto
        
        Args:
            instruction: Instrucción a validar
            
        Returns:
            True si es válida, False en caso contrario
        """
        valid_types = ["heading", "altitude", "speed", "flaps", "gear", "throttle"]
        
        if instruction.instruction_type not in valid_types:
            logger.warning(f"Invalid instruction type: {instruction.instruction_type}")
            return False
        
        if not instruction.parameters or "value" not in instruction.parameters:
            logger.warning("Instruction missing required parameters")
            return False
        
        return True
