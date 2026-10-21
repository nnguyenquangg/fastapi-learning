from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    country: str

@dataclass(frozen=True)
class Weather:
    location: Location
    temperature: float
    humidity: int
    wind_speed: float

    def format(self, width: int = 11) -> str:
        return (
            f"{self.location.name:<{width}}: "
            f"{self.temperature:.0f}°C, "
            f"humidity {self.humidity}%, "
            f"wind {self.wind_speed:.1f} m/s"
        )