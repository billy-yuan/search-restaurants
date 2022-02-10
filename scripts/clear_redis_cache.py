from database.redis_instance import redis_instance

if __name__ == "__main__":
    redis_instance.flushall()
