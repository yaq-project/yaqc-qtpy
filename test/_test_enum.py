from yaqd_core import IsDaemon


class TestEnum(IsDaemon):
    _kind = "test-enum"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self.rgb = "red"

    def get_rgb(self):
        return self.rgb

    def set_rgb(self, color):
        self.rgb = color


if __name__ == "__main__":
    TestEnum.main()
