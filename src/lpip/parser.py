"""
Lógica LLM (GPT-4o-mini) -> JSON
Parser de instrucciones usando LLM
"""

import json
import time
from typing import Optional, Dict, Any
from src.common.types import Instruction
from src.common.logger import get_logger
from src.context.context_database import ContextDatabase
from openai import OpenAI

logger = get_logger(__name__)


class InstructionParser:
    """
    Parsea instrucciones de lenguaje natural a formato JSON estructurado
    usando un LLM (GPT-4o-mini)
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.7, context_database: ContextDatabase = None):
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
        
        self.client = OpenAI(api_key=api_key)
    
    def _create_system_prompt(self) -> str:
        return f"""You are an ATC instruction parser.
  Your task is to extract:
  1. Callsign (normalized).
  2. Command (CLIMB, TURN, CONTACT, etc.).
  3. Value (normalized to integer).

  You must also construct reasonable response messages (readbacks). Be creative as to not be repetitive with the success and error messages.

  Take into account that text transcriptions may be faulty, and so you should try to infer the correct information based on the context.

  For example, if the text is "ryan air 559 blind and maintain 5000 feet", you should infer that the command is "ALTITUDE" and the value is 5000.

  CURRENT AIRCRAFTS IN THE CONTEXT DATABASE:
  {self.context_database.get_callsign_list()}

  SUPPORTED COMMANDS:
  {self.context_database.get_instructions_supported()}

Examples:
- "Iberia 559 climb and maintain 5000 feet" -> {"callsign": "IBE559", "command": "ALTITUDE", "value": 5000, "success_msg": "Roger that, IBE559 climbing to 5000 feet", "error_msg": "Station calling, say again, instruction unclear"}
- "Iberia 559 reduce speed to 180 knots" -> {"callsign": "IBE559", "command": "SPEED", "value": 180, "success_msg": "Roger that, IBE559 reducing speed to 180 knots", "error_msg": "Station calling, say again, instruction unclear"}

Return ONLY valid JSON, no additional text."""

    def _call_model(self, system_prompt: str, user_prompt: str) -> Optional[Instruction]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature
            )
            
            if not response.choices:
                logger.error("[ERROR] No response from model")
                return None
            
            content = response.choices[0].message.content
            
            if not content:
                logger.error("[ERROR] Empty response from model")
                return None
            
            # Parse JSON response
            try:
                instruction_data = json.loads(content)
                
                # Create Instruction object
                instruction = Instruction(
                    callsign=instruction_data.get("callsign"),
                    instruction_type=instruction_data.get("command"),
                    parameters=instruction_data.get("parameters", {}),
                    success_msg=instruction_data.get("success_msg"),
                    error_msg=instruction_data.get("error_msg")
                )
                
                return instruction
                
            except json.JSONDecodeError as e:
                logger.error(f"[ERROR] Failed to parse JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to call model: {e}")
            return None

    
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
            system_prompt = self._create_system_prompt()
            instruction = self._call_model(system_prompt, text)
            
            if not instruction:
                logger.error("[ERROR] Failed to parse instruction")
                return None
            
            if not self.validate_instruction(instruction):
                logger.error("[ERROR] Invalid instruction")
                return None
            
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
        valid_types = self.context_database.get_instructions_supported()
        
        if instruction.instruction_type not in valid_types:
            logger.warning(f"Invalid instruction type: {instruction.instruction_type}")
            return False
        
        if not instruction.parameters or "value" not in instruction.parameters:
            logger.warning("Instruction missing required parameters")
            return False
        
        return True
