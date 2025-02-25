from database import SessionLocal, AnimalInfo

def init_animal_info():
    db = SessionLocal()

    animals = [
        {
            "species_name": "gambusia_holbrooki",
            "common_name": "Sivrisinek Balığı",
            "description": "Sivrisinek larvaları ile beslenen küçük tatlı su balığı",
            "threat_level": "İstilacı Tür",
            "habitat": "Tatlı su"
        },
        {
            "species_name": "lepomis-gibbosus",
            "common_name": "Güneş Balığı",
            "description": "Belirgin benek desenli renkli tatlı su balığı",
            "threat_level": "Bazı bölgelerde istilacı",
            "habitat": "Tatlı su gölleri ve göletleri"
        },
        {
            "species_name": "siganus-rivulatus",
            "common_name": "Sokar Balığı",
            "description": "Mercan resiflerinde bulunan deniz balığı",
            "threat_level": "Lessepsian göçmen",
            "habitat": "Deniz, mercan resifleri"
        },
        {
            "species_name": "lagocephalus_sceleratus",
            "common_name": "Balon Balığı",
            "description": "Yüksek derecede zehirli balon balığı",
            "threat_level": "Tehlikeli - Zehirli",
            "habitat": "Deniz"
        },
        {
            "species_name": "pseudorasbora-parva",
            "common_name": "Çakıl Balığı",
            "description": "Küçük tatlı su balığı",
            "threat_level": "İstilacı Tür",
            "habitat": "Tatlı su"
        },
        {
            "species_name": "echinus_esculentus",
            "common_name": "Avrupa Yenilebilir Deniz Kestanesi",
            "description": "Büyük deniz kestanesi türü",
            "threat_level": "Tehlikeli Değil",
            "habitat": "Deniz, kayalık zeminler"
        }
    ]

    for animal in animals:
        db_animal = AnimalInfo(**animal)
        db.add(db_animal)

    db.commit()
    db.close()

if __name__ == "__main__":
    init_animal_info()