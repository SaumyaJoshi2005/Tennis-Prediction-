import Badge from "../common/Badge";

const statusColorMap = {
    LIVE: "green",
    IN_PROGRESS: "green",
    UPCOMING: "blue",
    SCHEDULED: "blue",
    PREDICTED: "green",
    COMPLETED: "gray",
    STALE: "gray",
    CANCELLED: "red",
};

function FixtureStatusBadge({ status }) {
    const normalizedStatus = (status || "SCHEDULED").toUpperCase();

    return (
        <Badge color={statusColorMap[normalizedStatus] || "blue"}>
            {normalizedStatus}
        </Badge>
    );
}

export default FixtureStatusBadge;
