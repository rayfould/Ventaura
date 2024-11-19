import React from 'react';

const Checkout = () => {
  return (
    <div className="sr-root">
      <div className="sr-main">
        <section className="container">
          <div>
            <h1>Add event to database</h1>
            <h4>Purchase a place on our website</h4>
            <div className="pasha-image">
              <img
                alt="Random asset from Picsum"
                src="https://thumbs.dreamstime.com/b/advertising-word-cloud-business-concept-56936998.jpg"
                width="140"
                height="160"
              />
            </div>
          </div>

          <form action="http://localhost:5152/api/create-checkout-session" method="POST">
            <button id="submit" role="link">Buy</button>
          </form>
        </section>
      </div>
    </div>
  );
};

export default Checkout;
