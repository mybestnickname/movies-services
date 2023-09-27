const dbName = "UGC_DB";
const conn = new Mongo();
const db = conn.getDB(dbName);

const collectionSettings = [

    {
        name: "FILM_RATINGS",
        shardKey: "user_id",
        indexFields: ["user_id","user_name", "movie_id", "score", "time_stamp"]
    },
        {
        name: "FILM_BOOKMARKS",
        shardKey: "film_id",
        indexFields: ["user_id", "film_id", "film_name", "timestamp"]
    },
    {
        name: "REVIEWS",
        shardKey: "film_id",
        indexFields: ["film_id", "text", "author", "timestamp", "update_timestamp"]
    },
    {
        name: "REVIEW_SCORES",
        shardKey: "review_id",
        indexFields: ["review_id", "author", "score", "timestamp"]
    },
    {
        name: "REVIEW_TO_FILM_SCORE",
        shardKey: "review_id",
        indexFields: ["review_id", "film_score_id"]
    },
];

sh.enableSharding(dbName);

collectionSettings.forEach((collection) => {
    const collectionName = collection.name;
    const shardKey = collection.shardKey;
    const indexFields = collection.indexFields;

    db.createCollection(collectionName);
    if (shardKey !== undefined) {
        sh.shardCollection(`${dbName}.${collectionName}`, {[shardKey]: "hashed"});
    }
    if (indexFields !== undefined) {
        indexFields.forEach((field) => {
            db[collectionName].createIndex({[field]: -1});
        })
    }
});
