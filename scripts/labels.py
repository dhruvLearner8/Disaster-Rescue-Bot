"""The allowed scenario labels, shared by the generator and the checker."""

ALLOWED = {
    "phase": {"before", "during", "after"},
    "urgency": {"critical", "high", "medium", "low"},
    "where": {"car", "house", "apartment", "basement", "rooftop", "small patch of land",
              "in the water", "campsite", "walking outside", "workplace", "school"},
    "who": {"alone", "kids", "baby", "elderly parent", "pet", "someone injured",
            "someone who can't swim", "strangers"},
    "complication": {"none", "power out", "phone battery low", "no car", "night time",
                     "injury", "medical condition", "doesn't speak English well"},
    "state": {"calm", "worried", "panicking", "shock"},
}
