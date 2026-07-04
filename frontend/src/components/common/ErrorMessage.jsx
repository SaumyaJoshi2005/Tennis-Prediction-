import "./ErrorMessage.css";

function ErrorMessage({

    message

}){

    return(

        <div className="error-box">

            <h3>

                Something went wrong

            </h3>

            <p>

                {message}

            </p>

        </div>

    );

}

export default ErrorMessage;