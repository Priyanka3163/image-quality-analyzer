import { ProductCarouselData } from '../../../data/ProductCarouselData';
import { useState } from 'react';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const ProductCarousel = () => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const maxVisibleItems = 4;
    const totalItems = ProductCarouselData.length;
    const maxIndex = Math.max(0, totalItems - maxVisibleItems);

    return (
        <div className="relative w-full">

            {/* Previous button */}
            {currentIndex > 0 && (
                <button
                    type="button"
                    className="
                        absolute left-2 top-1/2 z-20
                        -translate-y-1/2
                        w-10 h-10 rounded-full
                        bg-white shadow-md
                        flex items-center justify-center
                        text-blue-700
                        hover:bg-blue-50
                        transition
                    "
                    onClick={() => {
                        setCurrentIndex((prev) =>
                            Math.max(0, prev - 1)
                        );
                    }}
                >
                    <ArrowBackIcon />
                </button>
            )}


            {/* VIEWPORT */}
            <div className="overflow-hidden mx-14">

                {/* TRACK */}
                <div
                    className="
                        flex gap-4
                        transition-transform
                        duration-300
                        ease-in-out
                    "
                    style={{
                        transform: `translateX(calc(-${currentIndex} * ((100% + 1rem) / 4)))`
                    }}
                >

                    {/* CARDS */}
                    {ProductCarouselData.map((product, index) => (

                        <div
                            key={index}
                            className="
                                flex-[0_0_calc((100%-3rem)/4)]
                            "
                        >

                            {/* DaisyUI Card */}
                            <div className="card bg-base-100 w-full shadow-sm">

                                {/* Product image */}
                                <figure className="aspect-[3/2] bg-base-200">

                                    <img
                                        src={product.image}
                                        alt={product.name}
                                        className="w-full h-full object-cover"
                                    />

                                </figure>


                                {/* Card content */}
                                <div className="card-body">

                                    <div className="flex justify-between items-start gap-3">

                                        <h2 className="card-title text-base">
                                            {product.name}
                                        </h2>

                                        {/* Heart */}
                                        <button
                                            type="button"
                                            aria-label="Save product"
                                            title="Save this product"
                                            className="btn btn-ghost btn-circle btn-sm"
                                        >
                                            <i className="
                                                fa-regular
                                                fa-heart
                                                text-slate-400
                                                hover:text-red-500
                                                transition-colors
                                            " />
                                        </button>

                                    </div>


                                    <p className="text-sm text-slate-600">
                                        {product.description}
                                    </p>


                                    {/* Price + button */}
                                    <div className="card-actions items-center justify-between mt-2">

                                        <span className="text-xl font-bold text-slate-900">
                                            {product.price}
                                        </span>

                                        <button className="btn btn-primary btn-sm">
                                            Order now
                                        </button>

                                    </div>

                                </div>

                            </div>

                        </div>

                    ))}

                </div>
            </div>


            {/* Next button */}
            {currentIndex < maxIndex && (
                <button
                    type="button"
                    className="
                        absolute right-2 top-1/2 z-20
                        -translate-y-1/2
                        w-10 h-10 rounded-full
                        bg-white shadow-md
                        flex items-center justify-center
                        text-blue-700
                        hover:bg-blue-50
                        transition
                    "
                    onClick={() => {
                        setCurrentIndex((prev) =>
                            Math.min(maxIndex, prev + 1)
                        );
                    }}
                >
                    <ArrowForwardIcon />
                </button>
            )}

        </div>
    );
};

export default ProductCarousel;