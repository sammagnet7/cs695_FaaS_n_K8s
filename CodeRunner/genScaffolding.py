def generateScaffoldingWithEntrypoint(fnName: str):
    code = f"""from app import {fnName}
if __name__ == __main__:
    {fnName}()
"""
    return code


c = generateScaffoldingWithEntrypoint("userDefinedFunction")
print(c)
