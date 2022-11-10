import os
import pickle


class Cache:
    def __init__(self, key, update_function):
        self.key = key
        self.cache_dir = "_cache"
        self.update_function = update_function

    def get(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        cache_file = os.path.join(self.cache_dir, self.key)

        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return pickle.load(f)

        print(f"Updating {cache_file} cache")
        data = self.update_function()
        pickle.dump(data, open(cache_file, "wb"))

        return data
