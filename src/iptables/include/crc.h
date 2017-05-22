#define __pure			__attribute__((pure))
#define u8 __u8
#define u32 __u32

//LL: <crc stuff>
# define CRC_LE_BITS 32
# define CRC_BE_BITS 32
#define CRCPOLY_LE 0xedb88320
#define CRC32C_POLY_LE 0x82F63B78
#if CRC_LE_BITS > 8
# define LE_TABLE_ROWS (CRC_LE_BITS/8)
# define LE_TABLE_SIZE 256
#else
# define LE_TABLE_ROWS 1
# define LE_TABLE_SIZE (1 << CRC_LE_BITS)
#endif
static uint32_t crc32table_le[LE_TABLE_ROWS][256];
static uint32_t crc32ctable_le[LE_TABLE_ROWS][256];

#if CRC_LE_BITS > 8 || CRC_BE_BITS > 8
/* implements slicing-by-4 or slicing-by-8 algorithm */
static inline u32 __pure
crc32_body(u32 crc, unsigned char const *buf, size_t len, const u32 (*tab)[256])
{
# ifdef __LITTLE_ENDIAN
#  define DO_CRC(x) crc = t0[(crc ^ (x)) & 255] ^ (crc >> 8)
#  define DO_CRC4 (t3[(q) & 255] ^ t2[(q >> 8) & 255] ^ \
		   t1[(q >> 16) & 255] ^ t0[(q >> 24) & 255])
#  define DO_CRC8 (t7[(q) & 255] ^ t6[(q >> 8) & 255] ^ \
		   t5[(q >> 16) & 255] ^ t4[(q >> 24) & 255])
# else
#  define DO_CRC(x) crc = t0[((crc >> 24) ^ (x)) & 255] ^ (crc << 8)
#  define DO_CRC4 (t0[(q) & 255] ^ t1[(q >> 8) & 255] ^ \
		   t2[(q >> 16) & 255] ^ t3[(q >> 24) & 255])
#  define DO_CRC8 (t4[(q) & 255] ^ t5[(q >> 8) & 255] ^ \
		   t6[(q >> 16) & 255] ^ t7[(q >> 24) & 255])
# endif
	const u32 *b;
	size_t    rem_len;
# ifdef CONFIG_X86
	size_t i;
# endif
	const u32 *t0=tab[0], *t1=tab[1], *t2=tab[2], *t3=tab[3];
# if CRC_LE_BITS != 32
	const u32 *t4 = tab[4], *t5 = tab[5], *t6 = tab[6], *t7 = tab[7];
# endif
	u32 q;

	/* Align it */
	if ((long)buf & 3 && len) {
		do {
			DO_CRC(*buf++);
		} while ((--len) && ((long)buf)&3);
	}

# if CRC_LE_BITS == 32
	rem_len = len & 3;
	len = len >> 2;
# else
	rem_len = len & 7;
	len = len >> 3;
# endif

	b = (const u32 *)buf;
# ifdef CONFIG_X86
	--b;
	for (i = 0; i < len; i++) {
# else
	for (--b; len; --len) {
# endif
		q = crc ^ *++b; /* use pre increment for speed */
# if CRC_LE_BITS == 32
		crc = DO_CRC4;
# else
		crc = DO_CRC8;
		q = *++b;
		crc ^= DO_CRC4;
# endif
	}
	len = rem_len;
	/* And the last few bytes */
	if (len) {
		u8 *p = (u8 *)(b + 1) - 1;
# ifdef CONFIG_X86
		for (i = 0; i < len; i++)
			DO_CRC(*++p); /* use pre increment for speed */
# else
		do {
			DO_CRC(*++p); /* use pre increment for speed */
		} while (--len);
# endif
	}
	return crc;
#undef DO_CRC
#undef DO_CRC4
#undef DO_CRC8
}
#endif

static inline u32 __pure crc32_le_generic(u32 crc, unsigned char const *p,
					  size_t len, const u32 (*tab)[256],
					  u32 polynomial)
{
#if CRC_LE_BITS == 1
	int i;
	while (len--) {
		crc ^= *p++;
		for (i = 0; i < 8; i++)
			crc = (crc >> 1) ^ ((crc & 1) ? polynomial : 0);
	}
# elif CRC_LE_BITS == 2
	while (len--) {
		crc ^= *p++;
		crc = (crc >> 2) ^ tab[0][crc & 3];
		crc = (crc >> 2) ^ tab[0][crc & 3];
		crc = (crc >> 2) ^ tab[0][crc & 3];
		crc = (crc >> 2) ^ tab[0][crc & 3];
	}
# elif CRC_LE_BITS == 4
	while (len--) {
		crc ^= *p++;
		crc = (crc >> 4) ^ tab[0][crc & 15];
		crc = (crc >> 4) ^ tab[0][crc & 15];
	}
# elif CRC_LE_BITS == 8
	/* aka Sarwate algorithm */
	while (len--) {
		crc ^= *p++;
		crc = (crc >> 8) ^ tab[0][crc & 255];
	}
# else
	crc = ( u32) __cpu_to_le32(crc);
	crc = crc32_body(crc, p, len, tab);
	crc = __le32_to_cpu(( __le32)crc);
#endif
	return crc;
}
#if CRC_LE_BITS == 1
u32 __pure crc32_le(u32 crc, unsigned char const *p, size_t len)
{
	return crc32_le_generic(crc, p, len, NULL, CRCPOLY_LE);
}
u32 __pure __crc32c_le(u32 crc, unsigned char const *p, size_t len)
{
	return crc32_le_generic(crc, p, len, NULL, CRC32C_POLY_LE);
}
#else
u32 __pure crc32_le(u32 crc, unsigned char const *p, size_t len)
{
	return crc32_le_generic(crc, p, len,
			(const u32 (*)[256])crc32table_le, CRCPOLY_LE);
}
u32 __pure __crc32c_le(u32 crc, unsigned char const *p, size_t len)
{
	return crc32_le_generic(crc, p, len,
			(const u32 (*)[256])crc32ctable_le, CRC32C_POLY_LE);
}
#endif



//LL: </crc stuff>
