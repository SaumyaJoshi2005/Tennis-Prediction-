import "./PlayerAvatar.css";

function getInitials(name = "") {
    const parts = name.trim().split(/\s+/).filter(Boolean);

    if (parts.length === 0) {
        return "TP";
    }

    return parts.slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function PlayerAvatar({ player, size = "md" }) {
    const name = typeof player === "string" ? player : player?.player_name || player?.name || "Tennis Player";
    const imageUrl = typeof player === "object" ? player?.photo_url || player?.image_url || player?.avatar_url : null;

    return (
        <div className={`player-avatar player-avatar-${size}`} aria-label={name}>
            {imageUrl ? (
                <img src={imageUrl} alt={name} />
            ) : (
                <span>{getInitials(name)}</span>
            )}
        </div>
    );
}

export default PlayerAvatar;
