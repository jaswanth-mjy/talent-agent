import json
import sys

from core.agent import TalentAgent


def main():
    sample_jd = "Looking for Python backend developer with Django and SQL, 2 years experience"
    jd_text = " ".join(sys.argv[1:]).strip() or sample_jd

    try:
        agent = TalentAgent()
        output = agent.run(jd_text)
    except RuntimeError as error:
        print(f"Error: {error}")
        print("\nTo fix:")
        print("1) Start Ollama: ollama serve")
        print("2) Pull models: ollama pull llama3 && ollama pull nomic-embed-text")
        print("3) Retry this command")
        raise SystemExit(1)

    print("Parsed JD:")
    print(json.dumps(output["parsed_jd"], indent=2))
    print("\nRanked Shortlist:")
    print(json.dumps(output["results"], indent=2))


if __name__ == "__main__":
    main()