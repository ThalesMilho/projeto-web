const Pagination = function({ res = null, onPageChange }) {
    if (!res?.current_page) return null;

    const totalPages = res.last_page;
    const currentPage = res.current_page;

    return (
        <div className="flex text-white items-center justify-center space-x-2 mt-4">
            {[...Array(totalPages)].map((_, index) => {
                const pageNumber = index + 1;
                return (
                    <button
                        key={pageNumber}
                        onClick={() => onPageChange(pageNumber)}
                        className={`w-[40px] h-[40px] px-3 py-2 rounded-md bg-background font-bold ${currentPage === pageNumber ? "bg-primary text-white" : ""} `}
                    >
                        {pageNumber}
                    </button>
                );
            })}
        </div>
    );
}

export default Pagination;