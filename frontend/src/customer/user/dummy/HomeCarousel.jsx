import { useEffect, useState } from 'react';
import { HomeCarouselData } from '../../data/HomeCarouselData';

const Carousel = () => {
    const totalSlides = HomeCarouselData.length;

    // Add a clone of the last slide at the beginning
    // and a clone of the first slide at the end.
    const slides = [
        HomeCarouselData[totalSlides - 1],
        ...HomeCarouselData,
        HomeCarouselData[0],
    ];

    // Start at 1 because index 0 is the cloned last slide
    const [currentIndex, setCurrentIndex] = useState(1);
    const [isTransitioning, setIsTransitioning] = useState(true);

    const timeout = 3000;

    // Automatic sliding
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentIndex((prev) => prev + 1);
        }, timeout);

        return () => clearInterval(timer);
    }, []);

    // When we reach one of the cloned slides,
    // instantly reposition to the real slide.
    useEffect(() => {
        if (currentIndex === totalSlides + 1) {
            setTimeout(() => {
                setIsTransitioning(false);
                setCurrentIndex(1);
            }, 700);
        }

        if (currentIndex === 0) {
            setTimeout(() => {
                setIsTransitioning(false);
                setCurrentIndex(totalSlides);
            }, 700);
        }
    }, [currentIndex, totalSlides]);

    // Turn transition back on after the invisible reposition
    useEffect(() => {
        if (!isTransitioning) {
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    setIsTransitioning(true);
                });
            });
        }
    }, [isTransitioning]);

    const goToNext = () => {
        setCurrentIndex((prev) => prev + 1);
    };

    const goToPrevious = () => {
        setCurrentIndex((prev) => prev - 1);
    };

    return (
        <div className="relative w-full overflow-hidden">

            {/* Slides */}
            <div
                className={`flex ${
                    isTransitioning
                        ? 'transition-transform duration-700 ease-in-out'
                        : ''
                }`}
                style={{
                    transform: `translateX(-${currentIndex * 100}%)`,
                }}
            >
                {slides.map((item, index) => (
                    <div
                        key={index}
                        className="w-full flex-shrink-0"
                    >
                        <img
                            src={item.image}
                            alt={`Slide ${index + 1}`}
                            className="w-full h-86 md:h-106 object-fill"
                        />
                    </div>
                ))}
            </div>

            {/* Indicators */}
            <div className="absolute z-30 flex -translate-x-1/2 bottom-5 left-1/2 gap-3">
                {HomeCarouselData.map((_, index) => (
                    <button
                        key={index}
                        type="button"
                        className={`w-3 h-3 rounded-full transition ${
                            index === (currentIndex - 1 + totalSlides) % totalSlides
                                ? 'bg-white'
                                : 'bg-white/50'
                        }`}
                        aria-label={`Slide ${index + 1}`}
                        onClick={() => {
                            setIsTransitioning(true);
                            setCurrentIndex(index + 1);
                        }}
                    />
                ))}
            </div>

            {/* Previous */}
            <button
                type="button"
                onClick={goToPrevious}
                className="absolute top-0 left-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer"
            >
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 hover:bg-white/50 transition">
                    <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke="currentColor"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="m15 19-7-7 7-7"
                        />
                    </svg>
                </span>
            </button>

            {/* Next */}
            <button
                type="button"
                onClick={goToNext}
                className="absolute top-0 right-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer"
            >
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 hover:bg-white/50 transition">
                    <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke="currentColor"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="m9 5 7 7-7 7"
                        />
                    </svg>
                </span>
            </button>

        </div>
    );
};

export default Carousel;