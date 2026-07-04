import "./EmptyState.css";

function EmptyState({

    message

}){

    return(

        <div className="empty-state">

            <h3>

                Nothing to display

            </h3>

            <p>

                {message}

            </p>

        </div>

    );

}

export default EmptyState;