import "./Badge.css";

function Badge({

    children,

    color = "blue"

}){

    return(

        <span

            className={`badge badge-${color}`}

        >

            {children}

        </span>

    );

}

export default Badge;