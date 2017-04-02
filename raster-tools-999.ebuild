
EAPI=5

PYTHON_COMPAT=( python2_7 )

EGIT_REPO_URI="https://github.com/oldbay/raster_tools.git"
# EGIT_PROJECT="raster_tools-${PV}"
# EGIT_COMMIT=

PYTHON_DEPEND="2"

inherit distutils git-2

DESCRIPTION="Utilites for normalize and calculate georaster"
HOMEPAGE=""

LICENSE="GPL-2"
SLOT="0"
KEYWORDS=""

DEPEND="sci-libs/gdal"
RDEPEND="${DEPEND}"

python_install_all() {
        distutils_python_install_all

}
