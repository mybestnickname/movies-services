from services.recommendations import get_recommendations_service
from pkg.storage.ugc_service_storage import get_ugc_service_storage


def main():
    while True:
        ugc_storage = get_ugc_service_storage()
        recsys_service = get_recommendations_service()
        data = ugc_storage.get_all_scores()
        recsys_service.make_recommendations(data)


if __name__ == '__main__':
    main()
