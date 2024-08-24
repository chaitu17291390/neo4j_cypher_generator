from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union


from langchain_core.callbacks import CallbackManagerForChainRun

from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain


def extract_cypher(text: str) -> str:
    """Extract Cypher code from a text.

    Args:
        text: Text to extract Cypher code from.

    Returns:
        Cypher code extracted from the text.
    """
    # The pattern to find Cypher code enclosed in triple backticks
    pattern = r"```(.*?)```"

    # Find all matches in the input text
    matches = re.findall(pattern, text, re.DOTALL)

    return matches[0] if matches else text


class GraphCypherQAChainCustom(GraphCypherQAChain):

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Generate Cypher statement, use it to look up in db and answer question."""
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        question = inputs[self.input_key]
        args = {
            "question": question,
            "schema": self.graph_schema,
        }
        args.update(inputs)

        intermediate_steps: List = []

        generated_cypher = self.cypher_generation_chain.run(args, callbacks=callbacks)

        # Extract Cypher code if it is wrapped in backticks
        generated_cypher = extract_cypher(generated_cypher)
        intermediate_steps.append({"query": generated_cypher})

        try:
            # Correct Cypher query if enabled
            if self.cypher_query_corrector:
                generated_cypher = self.cypher_query_corrector(generated_cypher)

            _run_manager.on_text("Generated Cypher:", end="\n", verbose=self.verbose)
            _run_manager.on_text(
                generated_cypher, color="green", end="\n", verbose=self.verbose
            )

            # Retrieve and limit the number of results
            context = self.graph.query(generated_cypher)[: self.top_k]
            result_op = context
        except Exception as e:
            result_op = f"Error executing Cypher query: {str(e)}"

        return {
            "result": {
                "query": generated_cypher,
                "result_op": result_op
            },
            "intermediate_steps": intermediate_steps if self.return_intermediate_steps else None
        }

        @property
        def output_keys(self) -> List[str]:
            """Return the output keys.

            :meta private:
            """
            # Ensure 'result' key is expected in the output
            return ["result"]
