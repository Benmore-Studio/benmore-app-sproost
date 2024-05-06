document.addEventListener("DOMContentLoaded", () => {
    handleQuoteStatus();
})

const handleQuoteStatus = () => {
    // makes sure when the user clicks on the quote status, it doesn't redirect to the quote details page
    const QuoteContainer = document.getElementsByClassName('quoteContainer');
    var elementsArray = Array.from(QuoteContainer);
    elementsArray.forEach(function(element) {
        element.addEventListener('click', function(e){
            e.preventDefault();
        })
    });
}