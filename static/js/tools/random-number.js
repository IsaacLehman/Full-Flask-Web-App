(() => {
    const low_num = document.getElementById('low-end');
    const high_num = document.getElementById('high-end');
    const generate = document.getElementById('generate-btn');
    const error = document.querySelector('.error');
    const good = document.querySelector('.good');


    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function generateNum(low, high) {
        return Math.ceil((Math.random() * (high - low + 1)) + high);
    }

    generate.addEventListener('click', async () => {
        let cur_low = low_num.value;
        let cur_high = high_num.value;
        let num_to_generate = generateNum(4, 8);
        let sleep_start = 10;

        if (!cur_low || !cur_high || cur_low >= cur_high) {
            error.classList.remove('hide');
        } else {
            error.classList.add('hide');

            // Generate the animation
            let counter = 0;
            while (counter < num_to_generate) {

                good.innerHTML = generateNum(cur_low, cur_high);
                await sleep(sleep_start + sleep_start * counter);
                counter += 1;
            }
        }
    })
})();