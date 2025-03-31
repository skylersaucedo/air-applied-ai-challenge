from pathlib import Path


def generate_test_data():
    # Create test data directories
    base_dir = Path("test_data")
    directories = ["text", "image", "audio", "video"]

    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

    # Generate Shakespeare text sample
    shakespeare_text = """To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take Arms against a Sea of troubles,
And by opposing end them: to die, to sleep
No more; and by a sleep, to say we end
The heart-ache, and the thousand natural shocks
That flesh is heir to? 'Tis a consummation
Devoutly to be wished. To die, to sleep,
To sleep, perchance to Dream; aye, there's the rub,
For in that sleep of death, what dreams may come,
When we have shuffled off this mortal coil,
Must give us pause."""

    # Write Shakespeare text to file
    shakespeare_path = base_dir / "text" / "shakespeare_sample.txt"
    with open(shakespeare_path, "w", encoding="utf-8") as f:
        f.write(shakespeare_text)

    print(f"Generated Shakespeare text sample at {shakespeare_path}")


if __name__ == "__main__":
    generate_test_data()
