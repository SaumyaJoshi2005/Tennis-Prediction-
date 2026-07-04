import "./LoadingSpinner.css";

function LoadingSpinner({

    text = "Loading..."

}){

    return(

        <div className="loading">

            <div className="spinner"/>

            <p>

                {text}

            </p>

        </div>

    );

}

export default LoadingSpinner;