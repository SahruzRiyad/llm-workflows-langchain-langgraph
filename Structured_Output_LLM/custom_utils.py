# Simple class to track token usage.
class UsageTracker:
    input_tokens: list[int] = []
    output_tokens: list[int] = []
    total_tokens: list[int] = []

    def track(self, usage):
        self.input_tokens.append(usage.prompt_tokens)
        self.output_tokens.append(usage.completion_tokens)
        self.total_tokens.append(usage.total_tokens)

    def clear(self):
        self.input_tokens.clear()
        self.output_tokens.clear()
        self.total_tokens.clear()

    def __str__(self):
        return f"Inputs: {self.input_tokens}\nOutputs: {self.output_tokens}"