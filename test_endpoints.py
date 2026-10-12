import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test():
    print("Testing GET / ...")
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"GET / failed: {r.status_code}"
    print("GET / passed")

    print("Testing GET /api/student ...")
    r = requests.get(f"{BASE_URL}/api/student")
    assert r.status_code == 200
    student = r.json()["data"]
    print(f"Student: {student['name']}, Roll: {student['roll_no']}, Branch: {student['branch']}")

    print("Testing GET /api/experiments ...")
    r = requests.get(f"{BASE_URL}/api/experiments")
    assert r.status_code == 200
    exps = r.json()["data"]
    initial_count = len(exps)
    print(f"Total experiments loaded: {initial_count}")

    print("Testing POST /api/experiments (Add experiment) ...")
    payload = {
        "experiment_no": "4",
        "title": "Natural Language Processing with SpaCy",
        "short_description": "Tokenization, POS tagging, NER, and sentiment polarity scoring on customer feedback.",
        "d2_heading": "Experimental Procedure & Pipeline",
        "long_content": "AIM:\nTo implement NLP preprocessing pipelines.\n\nPROCEDURE:\n1. Clean text.\n2. Tokenize.\n\nCONCLUSION:\nExtracted entities successfully.",
        "github_url": "https://github.com/alexmorgan-ds/ds-lab-exp4"
    }
    r = requests.post(f"{BASE_URL}/api/experiments", data=payload)
    assert r.status_code == 201, f"Failed to add: {r.text}"
    new_exp = r.json()["data"]
    new_id = new_exp["id"]
    print(f"Added experiment ID: {new_id}, No: {new_exp['experiment_no']}")

    print("Testing Search for 'SpaCy' ...")
    r = requests.get(f"{BASE_URL}/api/experiments?q=SpaCy")
    assert r.status_code == 200
    search_data = r.json()["data"]
    assert len(search_data) >= 1
    print(f"Found {len(search_data)} matching experiment(s)")

    print("Testing Update Student Profile ...")
    update_data = {
        "name": "Alex Morgan",
        "roll_no": "22DS104",
        "section": "A",
        "branch": "Data Science & AI",
        "assistant_professor": "Dr. Rajesh Sharma",
        "github_url": "https://github.com/alexmorgan-ds/ds-lab-records"
    }
    r = requests.post(f"{BASE_URL}/api/student", data=update_data)
    assert r.status_code == 200
    updated_st = r.json()["data"]
    print(f"Updated student branch: {updated_st['branch']}")

    print(f"Testing DELETE /api/experiments/{new_id} ...")
    r = requests.delete(f"{BASE_URL}/api/experiments/{new_id}")
    assert r.status_code == 200
    print("Delete response:", r.json()["message"])

    r = requests.get(f"{BASE_URL}/api/experiments")
    assert len(r.json()["data"]) == initial_count
    print(f"Verified experiment count restored to {initial_count}")

    print("\nALL API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test()
