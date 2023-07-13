from dataclasses import dataclass, field


@dataclass
class Work:
    name: str
    photo_file_id: str = ""
    photo_hash: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "photo_file_id": self.photo_file_id,
            "photo_hash": self.photo_hash,
        }

    def is_filled(self) -> bool:
        return self.photo_file_id != ""


@dataclass
class Place:
    name: str
    works: list[Work] = field(default_factory=list)

    def to_dict(self):
        return {"name": self.name, "works": [work.to_dict() for work in self.works]}

    def is_filled(self):
        return all([work.is_filled() for work in self.works])


@dataclass
class CleaningDTO:
    places: list[Place] = field(default_factory=list)

    def to_dict(self):
        return {"places": [place.to_dict() for place in self.places]}

    def is_filled(self):
        return all([place.is_filled() for place in self.places])

    @staticmethod
    def from_dict(data: dict):
        cleaning_data = data["cleaning"]
        return CleaningDTO.from_db(cleaning_data)

    @staticmethod
    def from_db(data: dict):
        places_data = data["places"]
        places = []
        for place in places_data:
            works = []
            works_data = place["works"]

            for work in works_data:
                works.append(
                    Work(
                        name=work["name"],
                        photo_file_id=work["photo_file_id"],
                        photo_hash=work["photo_hash"],
                    )
                )
            places.append(Place(name=place["name"], works=works))

        return CleaningDTO(places=places)
