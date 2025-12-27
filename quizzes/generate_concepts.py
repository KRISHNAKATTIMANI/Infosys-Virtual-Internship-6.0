import json

# Use the exact subcategories from your modified data
subcategories_data = [
    {"pk": 35, "name": "Python"},
    {"pk": 36, "name": "Operating Systems"},
    {"pk": 42, "name": "Neural Networks"},
    {"pk": 43, "name": "NLP"},
    {"pk": 45, "name": "Anatomy & Physiology"},
    {"pk": 47, "name": "Diseases & Health Awareness"},
    {"pk": 106, "name": "Action"},
    {"pk": 107, "name": "Drama"},
    {"pk": 108, "name": "Rap"},
    {"pk": 109, "name": "Classical"},
    {"pk": 101, "name": "National"},
    {"pk": 102, "name": "International"},
    {"pk": 104, "name": "History"},
    {"pk": 105, "name": "Science"}
]

concept_bank = {
    "Python": {
        "easy": ["Variables", "Data Types", "Lists", "Tuples", "Dictionaries", "Sets", "If-Elif-Else", "For Loops", "While Loops", "Functions", "Comments", "Input/Output", "String Methods", "Slicing", "Boolean Logic", "Range Function", "Break/Continue", "Type Conversion", "Arithmetic Operators", "Indentation"],
        "medium": ["List Comprehensions", "Lambda Functions", "Map & Filter", "Modules", "File I/O", "Exception Handling", "Classes & Objects", "Inheritance", "Decorators", "Generators", "Iterators", "Virtual Environments", "PIP", "Args & Kwargs", "Magic Methods", "Context Managers", "Regular Expressions", "JSON Handling", "Date & Time", "Importing"],
        "hard": ["Metaclasses", "AsyncIO", "Multiprocessing", "Threading", "Memory Management", "GIL (Global Interpreter Lock)", "Descriptors", "Monkey Patching", "Cython", "Deep vs Shallow Copy", "Functional Programming", "Unit Testing", "Debugging", "Web Scraping", "Data Serialization", "Socket Programming", "Advanced Decorators", "Coroutines", "Typing Module", "Performance Optimization"]
    },
    "Operating Systems": {
        "easy": ["OS Definition", "Kernel Basics", "Types of OS", "Booting Process", "Process Concept", "Thread Concept", "GUI vs CLI", "File Extensions", "Directories", "System Calls", "User Mode", "Kernel Mode", "Batch Processing", "Multitasking", "Spooling", "Buffering", "Device Drivers", "BIOS", "Virtual Memory Basics", "Processors"],
        "medium": ["Process Scheduling", "CPU Scheduling Algos", "Deadlock Basics", "Semaphores", "Mutex", "Paging", "Segmentation", "File Systems (NTFS/EXT)", "Disk Scheduling", "Inter-process Communication", "Context Switching", "Swapping", "Thrashing", "Race Conditions", "Banker's Algorithm", "Memory Allocation", "Fragmentation", "Interrupts", "Shell Scripting", "Real-Time OS"],
        "hard": ["Distributed OS", "Microkernel vs Monolithic", "Deadlock Prevention", "Page Replacement Algos", "RAID Levels", "Security & Protection", "Virtualization", "Kernel Data Structures", "Socket Interface", "Distributed File Systems", "Memory Mapping", "I/O Subsystems", "Synchronization Primitives", "RTOS Scheduling", "Encryption in OS", "Network OS", "Cloud OS Concepts", "Hypervisors", "Containerization", "Kernel Compilation"]
    },
    "Neural Networks": {
        "easy": ["Biological Neuron", "Artificial Neuron", "Perceptron", "Inputs & Outputs", "Threshold", "Activation", "Binary Classification", "Weights Importance", "Bias Importance", "Feedforward", "Single Layer", "Multi Layer", "Training Concept", "Error Calculation", "Learning Concept", "Network Topology", "Synapse Concept", "History of NN"],
        "medium": ["Multilayer Perceptron (MLP)", "Gradient Descent", "Cost Function", "Backpropagation Algorithm", "Learning Rate Schedules", "Momentum", "Weight Initialization", "Hyperparameters", "Convergence", "Local Minima", "Universal Approximation", "Hidden Layer sizing", "Activation choices", "Training vs Validation", "Early Stopping", "Regularization", "Optimizers", "Softmax", "Cross-Entropy"],
        "hard": ["Hessian Matrix", "Second Order Methods", "Conjugate Gradient", "Levenberg-Marquardt", "Radial Basis Functions", "Hopfield Networks", "Boltzmann Machines", "Deep Belief Networks", "Spiking Neural Networks", "Hebbian Learning", "Competitive Learning", "Self-Organizing Maps (SOM)", "Adaptive Resonance Theory", "Neuro-Evolution", "Reservoir Computing", "Echo State Networks", "Liquid State Machines", "Dynamic Neural Fields", "Plasticity", "Neuromorphic Computing"]
    },
    "NLP": {
        "easy": ["NLP Definition", "Text Data", "Tokenization", "Stop Words", "Stemming", "Lemmatization", "Corpus", "Vocabulary", "Documents", "Sentences", "Parts of Speech", "Lowercasing", "Punctuation Removal", "Text Cleaning", "Language Detection", "Sentiment Analysis Basics", "Chatbot Basics", "Translation Basics", "Speech to Text", "Text to Speech"],
        "medium": ["Bag of Words", "TF-IDF", "N-Grams", "POS Tagging", "Named Entity Recognition (NER)", "Word Embeddings", "Word2Vec", "GloVe", "Cosine Similarity", "Text Classification", "Topic Modeling", "LDA", "Sentiment Analysis Advanced", "Dependency Parsing", "Syntax Trees", "Regular Expressions in NLP", "Text Summarization", "Language Models", "Spacy Library", "NLTK Library"],
        "hard": ["Transformers", "BERT", "GPT", "Attention Mechanism", "Encoder-Decoder", "Seq2Seq Models", "Machine Translation", "Question Answering", "Text Generation", "Contextual Embeddings", "Zero-Shot Learning", "Few-Shot Learning", "Coreference Resolution", "Semantic Role Labeling", "Knowledge Graphs", "Multilingual Models", "Fine-tuning LLMs", "Prompt Engineering", "Dialogue Systems", "Speech Processing"]
    },
    "Anatomy & Physiology": {
        "easy": ["Skeleton", "Skull", "Ribcage", "Spine", "Heartbeat", "Lungs", "Muscles", "Skin", "Digestion Basics", "Senses", "Bones", "Blood", "Nerves", "Organs", "Body Cavities", "Joints", "Breathing", "Pulse", "Growth", "Movement"],
        "medium": ["Digestive System", "Respiratory System", "Circulatory System", "Nervous System", "Endocrine System", "Reproductive System", "Urinary System", "Lymphatic System", "Homeostasis", "Metabolism", "Immune Response", "Blood Clotting", "Nerve Impulse", "Muscle Contraction", "Gas Exchange", "Hormone Action", "Kidney Function", "Sensory Perception", "Vision Mechanism", "Hearing Mechanism"],
        "hard": ["Neuroanatomy", "Cardiovascular Dynamics", "Respiratory Mechanics", "Renal Clearance", "Endocrine Feedback Loops", "Exercise Physiology", "High Altitude Physiology", "Diving Physiology", "Reproductive Cycles", "Fetal Physiology", "Aging Physiology", "Stress Physiology", "Pain Mechanisms", "Sleep Cycles", "Autonomic Control", "Signal Transduction", "Gene Expression", "Apoptosis", "Stem Cells", "Microanatomy"]
    },
    "Diseases & Health Awareness": {
        "easy": ["Common Cold", "Flu", "Fever", "Headache", "Cough", "Hygiene", "Vaccination Basics", "First Aid", "Healthy Diet", "Exercise Benefits", "Sleep Importance", "Hand Washing", "Germs", "Vitamins", "Water Intake", "Sun Safety", "Dental Care", "Mental Health Basics", "Stress Management", "Smoking Risks"],
        "medium": ["Diabetes", "Hypertension", "Asthma", "Allergies", "Infections", "Malaria", "Dengue", "Typhoid", "Tuberculosis", "COVID-19", "Obesity", "Heart Disease Risks", "Cancer Awareness", "Mental Disorders", "Addiction", "Antibiotic Resistance", "Immunization Schedule", "Nutrition Deficiencies", "Occupational Health", "Public Health"],
        "hard": ["Epidemiology", "Pandemics", "Genetic Disorders", "Autoimmune Diseases", "Neurological Disorders", "Cardiovascular Diseases", "Oncology", "HIV/AIDS", "Hepatitis", "Chronic Kidney Disease", "Rare Diseases", "Global Health Issues", "Health Policy", "Bioethics", "Telemedicine", "Personalized Medicine", "Clinical Trials", "Drug Development", "Healthcare Systems", "Preventive Medicine"]
    },
    "Action": {
        "easy": ["Stunts", "Explosions", "Chase Scenes", "Heroes", "Villains", "Fighting", "Weapons", "Speed", "Danger", "Rescues", "Martial Arts", "Car Chases", "Shootouts", "Superheroes", "Spies", "War", "Adventure", "Suspense", "Thrills", "Blockbusters"],
        "medium": ["Choreography", "Special Effects", "CGI", "Practical Effects", "Stunt Doubles", "Action Subgenres", "Buddy Cop", "Disaster Movies", "Heist Movies", "Revenge Movies", "Franchises", "Sequels", "Directing Action", "Editing Action", "Sound Design", "Pacing", "Tension", "Climax", "Resolution", "Iconic Roles"],
        "hard": ["Cinematography in Action", "History of Action", "Hong Kong Cinema", "Western Influence", "Action Stars Biographies", "Stunt Coordination", "Safety Regulations", "Budgeting Action", "Marketing Action", "Critical Reception", "Genre Evolution", "Deconstruction", "Parody", "Indie Action", "International Action", "Anime Action", "Motion Capture", "Virtual Production", "Impact on Culture", "Future of Action"]
    },
    "Drama": {
        "easy": ["Emotions", "Relationships", "Conflict", "Dialogue", "Characters", "Realism", "Sadness", "Happiness", "Love", "Family", "Friendship", "Tragedy", "Comedy-Drama", "Acting", "Script", "Story", "Plot", "Setting", "Theme", "Ending"],
        "medium": ["Character Development", "Plot Twists", "Subtext", "Monologues", "Screenwriting", "Directing Drama", "Acting Methods", "Awards", "Period Dramas", "Biopics", "Legal Dramas", "Medical Dramas", "Political Dramas", "Teen Dramas", "Indie Films", "Character Arcs", "Motifs", "Symbolism", "Foreshadowing", "Flashbacks"],
        "hard": ["Narrative Structures", "Cinematic Techniques", "Lighting & Mood", "Soundtracks", "Editing Rhythm", "Genre Blending", "Historical Accuracy", "Social Commentary", "Psychological Depth", "Method Acting", "Ensemble Casts", "Adaptations", "Play-to-Screen", "Directorial Styles", "Film Theory", "Criticism", "Audience Reception", "Cultural Impact", "Box Office", "Production Design"]
    },
    "Rap": {
        "easy": ["Rhyme", "Beat", "Flow", "Lyrics", "Rapper", "Hip Hop", "DJ", "Microphone", "Stage", "Concert", "Album", "Single", "Music Video", "Style", "Fashion", "Dance", "Graffiti", "Culture", "Street", "Voice"],
        "medium": ["Old School", "New School", "East Coast", "West Coast", "Freestyle", "Battle Rap", "Sampling", "Production", "Record Labels", "Mixtapes", "Collaborations", "Beefs", "Storytelling", "Metaphors", "Similes", "Punchlines", "Delivery", "Cadence", "Ad-libs", "Producers"],
        "hard": ["Lyricism", "Polyrhythms", "Internal Rhymes", "Multisyllabic Rhymes", "Social Conscious Rap", "Gangsta Rap", "Trap Music", "Mumble Rap", "Drill Music", "Global Hip Hop", "History of DJing", "Breakdancing Elements", "Graffiti Art", "Hip Hop Activism", "Business of Rap", "Streaming Era", "Independent vs Major", "Ghostwriting", "Sampling Laws", "Cultural Appropriation"]
    },
    "Classical": {
        "easy": ["Orchestra", "Piano", "Violin", "Composer", "Conductor", "Symphony", "Opera", "Ballet", "Music Notes", "Sheet Music", "Concert Hall", "Audience", "Instrument", "Melody", "Rhythm", "Harmony", "Tempo", "Volume", "Silence", "Applause"],
        "medium": ["Baroque Era", "Classical Era", "Romantic Era", "Modern Era", "Concerto", "Sonata", "String Quartet", "Choir", "Soloist", "Chamber Music", "Overture", "Aria", "Recitative", "Major Key", "Minor Key", "Scales", "Chords", "Dynamics", "Articulation", "Phrasing"],
        "hard": ["Bach", "Mozart", "Beethoven", "Tchaikovsky", "Chopin", "Vivaldi", "Handel", "Brahms", "Schubert", "Wagner", "Music Theory", "Counterpoint", "Fugue", "Orchestration", "Conducting Techniques", "Historical Performance", "Atonality", "Minimalism", "Opera Synopsis", "Instrument Families"]
    },
    "National": {
        "easy": ["President", "Prime Minister", "Capital City", "Flag", "Anthem", "Currency", "Language", "Population", "States", "Cities", "Holidays", "Festivals", "Food", "Clothes", "Sports", "Weather", "Map", "Borders", "Neighbors", "History Basics"],
        "medium": ["Constitution", "Parliament", "Elections", "Political Parties", "Laws", "Courts", "Economy", "Taxes", "Education System", "Healthcare System", "Transportation", "Infrastructure", "Agriculture", "Industry", "Tourism", "Media", "Culture", "Religion", "Minorities", "Immigration"],
        "hard": ["Foreign Policy", "Defense", "Budget", "GDP", "Inflation", "Trade", "Diplomacy", "Treaties", "Alliances", "Conflict Resolution", "Human Rights", "Environment Policy", "Energy Policy", "Science & Tech", "Space Program", "Social Issues", "Reforms", "Development", "Corruption", "Future Outlook"]
    },
    "International": {
        "easy": ["World Map", "Continents", "Oceans", "Countries", "Flags", "United Nations", "Peace", "War", "Trade", "Travel", "Passports", "Visas", "Languages", "Religions", "Currencies", "Time Zones", "Weather", "Climate", "Famous Places", "Global Events"],
        "medium": ["Geopolitics", "Diplomacy", "Embassies", "Consulates", "NGOs", "WHO", "WTO", "IMF", "World Bank", "NATO", "EU", "ASEAN", "G20", "G7", "International Law", "Human Rights", "Refugees", "Migration", "Terrorism", "Cybersecurity"],
        "hard": ["Globalization", "Climate Change", "Pandemics", "Economic Crisis", "Trade Wars", "Nuclear Proliferation", "Disarmament", "Peacekeeping", "Development Aid", "Debt Relief", "Sanctions", "Treaties", "Protocols", "Conventions", "Summits", "Resolutions", "Veto Power", "Sovereignty", "Diplomatic Immunity", "Extradition"]
    },
    "History": {
        "easy": ["Past", "Timeline", "Dates", "Events", "People", "Kings", "Queens", "Wars", "Peace", "Inventions", "Discoveries", "Explorers", "Ancient", "Modern", "Museums", "Books", "Stories", "Legends", "Myths", "Ruins"],
        "medium": ["Ancient Civilizations", "Egypt", "Rome", "Greece", "China", "India", "Middle Ages", "Renaissance", "Industrial Revolution", "World War I", "World War II", "Cold War", "Colonialism", "Independence", "Revolutions", "Civil Rights", "Women's Rights", "Democracy", "Dictators", "Empires"],
        "hard": ["Historiography", "Archaeology", "Anthropology", "Sociology", "Economic History", "Military History", "Political History", "Cultural History", "Art History", "Science History", "Philosophy", "Religion History", "Migration History", "Environmental History", "Oral History", "Primary Sources", "Secondary Sources", "Archives", "Preservation", "Heritage"]
    },
    "Science": {
        "easy": ["Nature", "Plants", "Animals", "Space", "Stars", "Planets", "Sun", "Moon", "Water", "Air", "Fire", "Earth", "Human Body", "Magnets", "Light", "Sound", "Electricity", "Machines", "Computers", "Robots"],
        "medium": ["Biology", "Chemistry", "Physics", "Astronomy", "Geology", "Ecology", "Environment", "Evolution", "Genetics", "Periodic Table", "Elements", "Compounds", "Mixtures", "Forces", "Motion", "Energy", "Waves", "Optics", "Thermodynamics", "Magnetism"],
        "hard": ["Quantum Physics", "Relativity", "Astrophysics", "Cosmology", "Particle Physics", "Nanotechnology", "Biotechnology", "Genetic Engineering", "Cloning", "Stem Cells", "Neuroscience", "Artificial Intelligence", "Robotics", "Space Exploration", "Mars Mission", "Climate Science", "Renewable Energy", "Nuclear Energy", "Material Science", "Theoretical Physics"]
    }
}

generic_concepts = {
    "easy": [f"Basic Concept {i}" for i in range(1, 21)],
    "medium": [f"Intermediate Concept {i}" for i in range(1, 21)],
    "hard": [f"Advanced Concept {i}" for i in range(1, 21)],
}

concepts_list = []
pk_counter = 2000 # Using a high start PK to avoid any leftover conflicts
timestamp = "2025-12-26T06:28:31.956Z"

for sub in subcategories_data:
    sub_pk = sub['pk']
    sub_name = sub['name']
    
    bank_entry = concept_bank.get(sub_name, generic_concepts)
    
    for difficulty in ['easy', 'medium', 'hard']:
        names_list = bank_entry.get(difficulty, generic_concepts[difficulty])
        
        # Track names used for THIS specific subcategory + difficulty
        seen_in_group = set()
        
        for i in range(20):
            original_name = names_list[i % len(names_list)]
            current_name = original_name
            
            # If name is a duplicate within this subcategory/difficulty, add a suffix
            counter = 1
            while current_name in seen_in_group:
                current_name = f"{original_name} ({counter})"
                counter += 1
            
            seen_in_group.add(current_name)
            
            concepts_list.append({
                "model": "quizzes.concept",
                "pk": pk_counter,
                "fields": {
                    "subcategory": sub_pk,
                    "difficulty": difficulty,
                    "name": current_name,
                    "created_at": timestamp
                }
            })
            pk_counter += 1

with open("concepts.json", "w") as f:
    json.dump(concepts_list, f, indent=2)