import factory


class UserPayloadFactory(factory.Factory):


    class Meta:
        model = dict

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password_hash = "test-password"
    full_name = factory.Sequence(lambda n: f"Test User {n}")
