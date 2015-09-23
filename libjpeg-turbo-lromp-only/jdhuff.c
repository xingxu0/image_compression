/*
 * jdhuff.c
 *
 * This file was part of the Independent JPEG Group's software:
 * Copyright (C) 1991-1997, Thomas G. Lane.
 * libjpeg-turbo Modifications:
 * Copyright (C) 2009-2011, D. R. Commander.
 * For conditions of distribution and use, see the accompanying README file.
 *
 * This file contains Huffman entropy decoding routines.
 *
 * Much of the complexity here has to do with supporting input suspension.
 * If the data source module demands suspension, we want to be able to back
 * up to the start of the current MCU.  To do this, we copy state variables
 * into local working storage, and update them back to the permanent
 * storage only upon successful completion of an MCU.
 */

#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"
#include "jdhuff.h"             /* Declarations shared with jdphuff.c */
#include "jpegcomp.h"
#include "jstdhuff.c"
#include "limits.h"
#include "jpeg_nbits_table.h"

signed char lumi_huff_code[256] = {4 , 2 , 2 , 3 , 4 , 5 , 7 , 8 , 10 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 4 , 5 , 7 , 9 , 11 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 5 , 8 , 10 , 12 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 6 , 9 , 12 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 6 , 10 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 7 , 11 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 7 , 12 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 8 , 12 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 15 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 10 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 10 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 11 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , 11 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1};
signed char chro_huff_code[256] = {2 , 2 , 3 , 4 , 5 , 5 , 6 , 7 , 9 , 10 , 12 , -1 , -1 , -1 , -1 , -1 , -1 , 4 , 6 , 8 , 9 , 11 , 12 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 5 , 8 , 10 , 12 , 15 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 5 , 8 , 10 , 12 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 6 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 6 , 10 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 7 , 11 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 7 , 11 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 8 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 9 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 11 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , -1 , 14 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1 , -1 , 10 , 15 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , 16 , -1 , -1 , -1 , -1};

unsigned char lumi_quant[64] = {16,  11,  10,  16,  24,  40,  51,  61,
  12,  12,  14,  19,  26,  58,  60,  55,
  14,  13,  16,  24,  40,  57,  69,  56,
  14,  17,  22,  29,  51,  87,  80,  62,
  18,  22,  37,  56,  68, 109, 103,  77,
  24,  35,  55,  64,  81, 104, 113,  92,
  49,  64,  78,  87, 103, 121, 120, 101,
  72,  92,  95,  98, 112, 100, 103,  99};

unsigned char chro_quant[64] = {17,  18,  24,  47,  99,  99,  99,  99,
  18,  21,  26,  66,  99,  99,  99,  99,
  24,  26,  56,  99,  99,  99,  99,  99,
  47,  66,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99};


// entropy table initialization - Xing
inline int get_bin(int * bin, int bins, int f) {
	int i;
	for (i=0; i<=bins; ++i)
		if (f < bin[i])
			return i;
	return bins;

/*
	register int l = 0, r = bins, m;
	while (l < r) {
		m = (l + r) >> 1;
		if (f < bin[m])
			r = m;
		else l = m + 1;
	}
	return l;
	*/
}

inline int get_bin_naive(int *bin, int f) {
  if (f < bin[10]) {
	  if (f < bin[4]) {
		  if (f < bin[0]) return 0;
		  if (f < bin[1]) return 1;
		  if (f < bin[2]) return 2;
		  if (f < bin[3]) return 3;
		  return 4;
	  } else {
		  if (f < bin[5]) return 5;
		  if (f < bin[6]) return 6;
		  if (f < bin[7]) return 7;
		  if (f < bin[8]) return 8;
		  if (f < bin[9]) return 9;
		  return 10;
	  }
  }
  else {
	  if (f < bin[15]) {
		  if (f < bin[11]) return 11;
		  if (f < bin[12]) return 12;
		  if (f < bin[13]) return 13;
		  if (f < bin[14]) return 14;
		  return 15;
	  } else {
		  if (f < bin[16]) return 16;
		  if (f < bin[17]) return 17;
		  if (f < bin[18]) return 18;
		  if (f < bin[19]) return 19;
		  if (f < bin[20]) return 20;
		  return 20;
	  }
  }
}

inline int get_dc_index(int ci, previous_block_state_t * previous_block_state, int index1, int index2) {
	int s=0, t=0, temp, temp3;
	//int now_index = previous_block_state->current_index[ci];
	JCOEF *b = previous_block_state->previous_blocks[ci];
	//for (i=0; i<2; ++i) {
  //now_index = now_index == 0 ? LOOK_BACKWARD_BLOCK - 1 : now_index - 1;
  temp = b[index1];
  if (temp) {
	  //t += 1;
	  //t -= 2*(((unsigned int)temp)>>31);
	  if (temp < 0) t-=1;
	  else t+=1;
	  temp3 = temp >> (CHAR_BIT * sizeof(int) - 1); \
	  temp ^= temp3; \
	  temp -= temp3; \
	  s += temp;
  }

  //now_index = now_index == 0 ? LOOK_BACKWARD_BLOCK - 1 : now_index - 1;
  temp = b[index2];
  if (temp) {
	  //t += 1;
	  //t -= 2*(((unsigned int)temp)>>31);
	  if (temp < 0) t-=1;
	  else t+=1;
	  temp3 = temp >> (CHAR_BIT * sizeof(int) - 1); \
	  temp ^= temp3; \
	  temp -= temp3; \
	  s += temp;
  }

	s>>=1;
	if (t) {
		//s += 24;
		//s -= 12*(((unsigned int)t)>>31);
		if (t<0) s+=12;
		else s+=24;
		return s;
	}
	else return s;
}

inline int get_first_dimension_index(int ci, int pos, int f, int dc_diff) {
	if (pos == 1)
		f = (dc_diff > 10 ? 10 : dc_diff)*1000/11;
		//return dc_diff > 10 ? 10 : dc_diff;
	//return get_bin(coef_bins[ci][pos], first_dimension_bins, f);
	return get_bin_naive(coef_bins[ci][pos], f);
	/*
	for (int i = 0; i < first_dimension_bins; ++i)
		if (f < coef_bins[ci].bins[pos][i])
			return i;
	return first_dimension_bins;
	*/
}

inline int get_second_dimension_index(int ci, int pos, previous_block_state_t * previous_block_state, int index1, int index2, int index3) {
	//int i;
	int l;
	register int k, su = 0, ma = 0;
	l = pos + LOOK_FORWARD_COEF > 64 ? 64 : pos + LOOK_FORWARD_COEF;
	UINT16* max_table = max_pos_value_range[ci][pos];
	UINT8 (*avgs_)[64] = previous_block_state->previous_blocks_avgs[ci];
	UINT8 (*ma_)[64] = previous_block_state->previous_blocks_avgs_ma[ci];
	//for (i=0; i<LOOK_BACKWARD_BLOCK; ++i) {

	// for 3 times
		//if (previous_block_state->previous_blocks_avgs[ci][now_index][pos] != -1) {
			k = avgs_[index1][pos];
			su += k;
			if (k != 0)
			  ma += ma_[index1][pos];
			else
		      ma += max_table[l];

			    //if (previous_block_state->previous_blocks_avgs[ci][now_index][pos] != -1) {
			      k = avgs_[index2][pos];
			      su += k;
			      if (k != 0)
			        ma += ma_[index2][pos];
			      else
			          ma += max_table[l];

			          //if (previous_block_state->previous_blocks_avgs[ci][now_index][pos] != -1) {
			            k = avgs_[index3][pos];
			            su += k;
			            if (k != 0)
			              ma += ma_[index3][pos];
			            else
			                ma += max_table[l];
		/*
		}
		else {
			for (j=pos; j<l; ++j) {
				k = previous_block_state->previous_blocks[ci][now_index][j];
				if (k) break;
			}

			su += k;
			if (j == l) --j;
			temp_ma = max_pos_value_range[ci].bits[pos][j];

			//if (k!=0 && temp_ma != previous_block_state->previous_blocks_avgs_ma[ci][now_index][pos]) printf("-");
			ma += temp_ma;
			previous_block_state->previous_blocks_avgs[ci][now_index][pos] = k;
			previous_block_state->previous_blocks_avgs_ma[ci][now_index][pos] = temp_ma;
		}
	*/
	//}

	//return get_bin(coef_bins_p[ci][pos], second_dimension_bins, f);
	return get_bin_naive(coef_bins_p[ci][pos], su*1000/ma);
}

/*
inline int get_second_dimension_index(int ci, int pos, previous_block_state_t * previous_block_state, int dc_diff_bits) {
	int now_index = previous_block_state->current_index[ci];
	int i, j, k, l, su = 0, current_dc_diff = dc_diff_bits, times = 0;
	int limit = previous_block_state->total_blocks[ci];
	if (limit > LOOK_BACKWARD_BLOCK) limit = LOOK_BACKWARD_BLOCK;
	for (i=0; i<limit; ++i) {
		now_index = now_index == 0 ? LOOK_BACKWARD_BLOCK - 1 : now_index - 1;
		if (current_dc_diff > 5) break; // may cancel this line later
#ifdef DEBUG
		printf("%d:%d,%d,%d,%d\n", current_dc_diff, previous_block_state->previous_blocks[ci][now_index][1],
				previous_block_state->previous_blocks[ci][now_index][2],
				previous_block_state->previous_blocks[ci][now_index][3],
				previous_block_state->previous_blocks[ci][now_index][4]);
#endif

		++times;
		if (previous_block_state->previous_blocks_avgs[ci][now_index][pos] != -1)
			su += previous_block_state->previous_blocks_avgs[ci][now_index][pos];
		else {
			k = 0;
			l = pos + LOOK_FORWARD_COEF > 64 ? 64 : pos + LOOK_FORWARD_COEF;
			for (j=pos; j<l; ++j)
			{
				k += previous_block_state->previous_blocks[ci][now_index][j];
			}
			su += k;
			previous_block_state->previous_blocks_avgs[ci][now_index][pos] = k;
		}
		current_dc_diff = previous_block_state->previous_blocks[ci][now_index][0];
	}
	if (times == 0)
		return 15 + dc_diff_bits;

	int f = su*1000/(times*previous_blocks_max_avgs[ci][pos]);
#ifdef DEBUG
	printf("second dimension: %d, %d, %f\n", su, previous_blocks_max_avgs[ci][pos], f);
#endif
	return get_bin(coef_bins_p[ci].bins[pos], second_dimension_bins, f);
}*/

int ts = 0;
void get_derived_huff_table_c(symbol_table_c* output_tbl)
{
	symbol_table_tmp * tbl = &table_tmp;
	int lastp, p, l, code, si, i, entries = tbl->length;
	int * bits_aggre = malloc((entropy_max_AC_bits + 1)*sizeof(int));
	char huffsize[entries + 1];
	//unsigned int huffcode[entries + 1];
	int huffcode[entries + 1];

	p = 0;
	i = 0;
	for (l = 0; l <= entropy_max_AC_bits; l++)
		bits_aggre[l] = 0;
	for (l = 1; l <= entropy_max_AC_bits; l++)
	{
		if (tbl->bits[i] < l) i++;
		while (i < entries && tbl->bits[i] == l)
		{
			bits_aggre[l] ++;
			i++;
		}
		if (i == entries) break;
	}
	for (l = 1; l <= entropy_max_AC_bits; l++) {
		i = (int) bits_aggre[l];
		while (i--)
			huffsize[p++] = (char) l;
	}
	huffsize[p] = 0;
	lastp = p;

	code = 0;
	si = huffsize[0];
	p = 0;
	while (huffsize[p]) {
		while (((int) huffsize[p]) == si) {
			huffcode[p++] = code;
			code++;
		}
		code <<= 1;
		si++;
	}

	for (p = 0; p < lastp; p++) {
		i = tbl->run_length == NULL ? p : tbl->run_length[p];
		output_tbl->symbol[i] = huffcode[p];
		output_tbl->bits[i] = huffsize[p];
	}
  free(bits_aggre);
}

void get_derived_huff_table_d(symbol_table_d* output_tbl)
{
	symbol_table_tmp * tbl = &table_tmp;
	int lastp, p, l, code, si, i, entries = tbl->length, lookbits, ctr;
	int * bits_aggre = malloc((entropy_max_AC_bits + 1)*sizeof(int));
	char huffsize[entries + 1];
	//unsigned int huffcode[entries + 1];
	int huffcode[entries + 1];

	p = 0;
	i = 0;
	for (l = 0; l <= entropy_max_AC_bits; l++)
		bits_aggre[l] = 0;
	for (l = 1; l <= entropy_max_AC_bits; l++)
	{
		if (tbl->bits[i] < l) i++;
		while (i < entries && tbl->bits[i] == l)
		{
			bits_aggre[l] ++;
			i++;
		}
		if (i == entries) break;
	}
	for (l = 1; l <= entropy_max_AC_bits; l++) {
		i = (int) bits_aggre[l];
		while (i--)
			huffsize[p++] = (char) l;
	}
	huffsize[p] = 0;
	lastp = p;

	code = 0;
	si = huffsize[0];
	p = 0;
	while (huffsize[p]) {
		while (((int) huffsize[p]) == si) {
			huffcode[p++] = code;
			code++;
		}
		code <<= 1;
		si++;
	}

	for (p = 0; p < lastp; p++) {
		i = output_tbl->run_length == NULL ? p : tbl->run_length[p];
		tbl->symbol[i] = huffcode[p];
		tbl->bits[i] = huffsize[p];
	}

	p = 0;
	for (l = 1; l <= entropy_max_AC_bits; l++) {
		if (bits_aggre[l]) {
			/* valoffset[l] = huffval[] index of 1st symbol of code length l,
			 * minus the minimum code of length l
			 */
			output_tbl->valoffset[l] = (INT32) p - (INT32) huffcode[p];
			p += bits_aggre[l];
			output_tbl->max_bits[l] = huffcode[p-1]; /* maximum code of length l */
		} else {
			output_tbl->max_bits[l] = -1;	/* -1 if no codes of this length */
		}
	}
	output_tbl->max_bits[entropy_max_AC_bits + 1] = 0xFFFFFL; /* ensures jpeg_huff_decode terminates */

  for (i = 0; i < (1 << HUFF_LOOKAHEAD_ENTROPY); i++)
    //output_tbl->lookup[i] = (HUFF_LOOKAHEAD_ENTROPY + 1) << HUFF_LOOKAHEAD_ENTROPY;
	output_tbl->lookup[i] = (HUFF_LOOKAHEAD_ENTROPY + 1) << 8;

  p = 0;
  for (l = 1; l <= HUFF_LOOKAHEAD_ENTROPY; l++) {
    for (i = 1; i <= (int) bits_aggre[l]; i++, p++) {
      /* l = current code's length, p = its index in huffcode[] & huffval[]. */
      /* Generate left-justified code followed by all possible bit sequences */
    	lookbits = huffcode[p] << (HUFF_LOOKAHEAD_ENTROPY-l);
      for (ctr = 1 << (HUFF_LOOKAHEAD_ENTROPY-l); ctr > 0; ctr--) {
      	//output_tbl->lookup[lookbits] = (l << HUFF_LOOKAHEAD_ENTROPY) | output_tbl->run_length[p];
      	output_tbl->lookup[lookbits] = (l << 8) | output_tbl->run_length[p];
        lookbits++;
      }
    }
  }

  free(bits_aggre);
}

boolean default_table[3];
int default_i[3];
int default_j[3];
int default_k[3];
boolean initialize_AC_table(int c, int i, int j, int k, int private_option)
{
	int table_size = 256;
	char filename[200];
	sprintf(filename, "%s/%d/plain_%d_%d_%d.table", table_folder, c, i, j, k);
	FILE * f = fopen(filename, "r");
	if (f == NULL) {

		if (default_table[c]) {
			if (private_option == 1)
				memcpy(&ac_table[c][i][j][k], &ac_table[c][default_i[c]][default_j[c]][default_k[c]], sizeof(symbol_table_c));
			else
				memcpy(&ac_table_d[c][i][j][k], &ac_table_d[c][default_i[c]][default_j[c]][default_k[c]], sizeof(symbol_table_d));
			return TRUE;
		}

		sprintf(filename, "%s/%d/plain_%d_%d_%d.table", table_folder, c, 100,100,100);
				f = fopen(filename, "r");
				default_table[c] = TRUE;
				default_i[c] = i;
				default_j[c] = j;
				default_k[c] = k;

				if (f==NULL) {
					printf("%d %d %d %d ", c,i,j,k);
					printf("ac still null\n");
					return FALSE;
				}
	}

	ts += 1;
	table_tmp.length = table_size;
	int ii;
	if (private_option == 1) {
		ac_table[c][i][j][k].symbol = malloc(table_size*sizeof(int));
		for (ii = 0; ii< table_size; ++ii)
			ac_table[c][i][j][k].symbol[ii] = -1;
		ac_table[c][i][j][k].bits = malloc(table_size*sizeof(UINT8));
		for (ii = 0; ii < table_size; ++ii)
		{
			int ret = fscanf(f, "%d: %d", &(table_tmp.bits[ii]), &(table_tmp.run_length[ii]));
			ac_table[c][i][j][k].bits[ii] = table_tmp.bits[ii];
			if (! ret) continue;
			if (ac_table[c][i][j][k].bits[ii] >= entropy_max_AC_bits) printf("!!! AC %d %d %d more bits than expected\n", i, j, k);
			//if (ac_table[c][i][j].bits > 16) printf("Larger table %d %d %d\n", c, i, j);
		}
		fclose(f);
		get_derived_huff_table_c(&(ac_table[c][i][j][k]));
	} else {
		ac_table_d[c][i][j][k].max_bits = malloc((entropy_max_AC_bits + 2)*sizeof(int));
		ac_table_d[c][i][j][k].valoffset = malloc((entropy_max_AC_bits + 2)*sizeof(int));
		ac_table_d[c][i][j][k].run_length = malloc(table_size*sizeof(UINT8));
		for (ii = 0; ii < table_size; ++ii)
		{
			int ret = fscanf(f, "%d: %d", &(table_tmp.bits[ii]), &(table_tmp.run_length[ii]));
			ac_table_d[c][i][j][k].run_length[ii] = table_tmp.run_length[ii];
			if (! ret) continue;
			if (table_tmp.bits[ii] >= entropy_max_AC_bits) printf("!!! AC %d %d %d more bits than expected\n", i, j, k);
			//if (ac_table[c][i][j].bits > 16) printf("Larger table %d %d %d\n", c, i, j);
		}
		fclose(f);
		get_derived_huff_table_d(&(ac_table_d[c][i][j][k]));
	}
	//for printing...

	
/*
		printf("Look ahead table:\n");
		for (int ii=0; ii<(1<<HUFF_LOOKAHEAD); ++ii) {
			printf("\t%d: %d, %d\n", ii, ac_table[c][i][j][k].look_nbits[ii], ac_table[c][i][j][k].look_sym[ii]);
		}*/

	return TRUE;
}

void initialize_DC_table(int c, int i, int private_option)
{
	char filename[200];
	int table_size = 25;
	sprintf(filename, "%s/%d/plain_DC_%d_.table", table_folder, c, i);
	FILE * f = fopen(filename, "r");
	if (f == NULL) {
		sprintf(filename, "%s/%d/plain_DC_%d_.table", table_folder, c, 100);
		f = fopen(filename, "r");

		if (f==NULL) {
			printf("dc still null\n");
			return;
		}
	}

	int ii;
	table_tmp.length = table_size;
	if (private_option == 1) {
		dc_table[c][i].symbol = malloc(table_size*sizeof(int));
		for (ii = 0; ii< table_size; ++ii)
			dc_table[c][i].symbol[ii] = -1;
		dc_table[c][i].bits = malloc(table_size*sizeof(UINT8));
		for (ii = 0; ii < table_size; ++ii)
		{
			int ret = fscanf(f, "%d: %d", &(table_tmp.bits[ii]), &(table_tmp.run_length[ii]));
			dc_table[c][i].bits[ii] = table_tmp.bits[ii];
			if (! ret) continue;
			if (dc_table[c][i].bits[ii] >= entropy_max_AC_bits) printf("!!! DC %d %d more bits than expected 1!\n", c, i);
		}
		fclose(f);
		get_derived_huff_table_c(&(dc_table[c][i]));
	} else {
		dc_table_d[c][i].max_bits = malloc((entropy_max_AC_bits + 2)*sizeof(int));
		dc_table_d[c][i].valoffset = malloc((entropy_max_AC_bits + 2)*sizeof(int));
		dc_table_d[c][i].run_length = malloc(table_size*sizeof(UINT8));
		for (ii = 0; ii < table_size; ++ii)
		{
			int ret = fscanf(f, "%d: %d", &(table_tmp.bits[ii]), &(table_tmp.run_length[ii]));
			dc_table_d[c][i].run_length[ii] = table_tmp.run_length[ii];
			if (! ret) continue;
			if (table_tmp.bits[ii] >= entropy_max_AC_bits) printf("!!! DC %d %d more bits than expected 2!\n", c, i);
		}
		fclose(f);
		get_derived_huff_table_d(&(dc_table_d[c][i]));
	}
/*
	if (c==2) {
		printf("dc table...\r\n");
		for (ii = 0; ii < 23; ++ii)
		{
			printf("%d:%d:%d \r\n", ii, dc_table[c][i].bits[ii], dc_table[c][i].symbol[ii]);
		}
	}
	*/
}


void initialize_max_pos_value(int c)
{
	char filename[200];
	sprintf(filename, "%s/plain_max_pos_value_%d", table_folder, c);
	FILE * f = fopen(filename, "r");
	if (f == NULL) return;

	int a, b, i, j, k;
	for (i=0; i<64; ++i) {
		int ret = fscanf(f, "%d: %d", &a, &b);
		if (! ret) continue;
		max_pos_value[c][a] = b;
	}
	fclose(f);

	int t = 0;
	for (i=0; i<64; ++i)
			for (j=0; j<65; ++j)
				max_pos_value_range[c][i][j] = 1;

	for (i=0; i<64; ++i) {
		for (j=i; j<64; ++j) {
			t = 1;
			for (k=i; k<=j; ++k)
				t += max_pos_value[c][k];
			if (t>511) t=511;
			max_pos_value_range[c][i][j+1] = t;
			if (t>255) t=255;
			max_pos_value_range_r[c][j][i] = t;
		}
	}

/*
	if (c==2) {
			printf("max_pos table...\r\n");
			for (int ii = 0; ii < 64; ++ii)
			{
				printf("%d:%d \r\n", ii, max_pos_value[c].bits[ii]);
			}
		}
		*/
}

void initialize_coef_bins(int c)
{
	char filename[200];
	sprintf(filename, "%s/plain_coef_bins_1_%d", table_folder, c);
	FILE * f = fopen(filename, "r");
	if (f == NULL) return;

	int a;
	float b;
	int i, j;
	for (i=1; i<=63; ++i) {
		int ret = fscanf(f, "%d: ", &a);
		if (! ret) continue;
		coef_bins[c][a] = malloc((first_dimension_bins + 1)*sizeof(float));
		for (j=0; j<first_dimension_bins; ++j) {
			ret = fscanf(f, "%f ", &b);
			if (! ret) continue;
			coef_bins[c][a][j] = (int)(b*1000);
		}
		coef_bins[c][a][first_dimension_bins] = INT_MAX;
	}
	fclose(f);

	/*
	if (c==0) {
		printf("coef_bins table...\r\n");
		for (int ii = 0; ii < 64; ++ii)
		{
			printf("%d:", ii);
			for (int jj=0; jj<20; ++jj)
				printf("%f ", coef_bins[c].bins[ii][jj]);
			printf("\n");
		}
	}
	*/
}

void initialize_coef_bins_p(int c)
{
	char filename[200];
	sprintf(filename, "%s/plain_coef_bins_9_%d", table_folder, c);
	FILE * f = fopen(filename, "r");
	if (f == NULL) return;

	int a, i, j;
	float b;
	for (i=1; i<=63; ++i) {
		int ret = fscanf(f, "%d: ", &a);
		if (! ret) continue;
		coef_bins_p[c][a] = malloc((second_dimension_bins + 1)*sizeof(float));
		for (j=0; j<second_dimension_bins; ++j) {
			ret = fscanf(f, "%f ", &b);
			if (! ret) continue;
			coef_bins_p[c][a][j] = (int)(b*1000);
		}
	}
	fclose(f);

/*
	if (c==0) {
		printf("coef_bins table...\r\n");
		for (int ii = 0; ii < 64; ++ii)
		{
			printf("%d:", ii);
			for (int jj=0; jj<20; ++jj)
				printf("%f ", coef_bins_p[c].bins[ii][jj]);
			printf("\n");
		}
	}
	*/
}

void entropy_table_initialization(int private_option)
{
	int table_size = 256;
	entropy_max_AC_bits = 32;

	table_tmp.symbol = malloc(table_size*sizeof(int));
	int ii;
	for (ii = 0; ii< table_size; ++ii)
		table_tmp.symbol[ii] = -1;
	table_tmp.bits = malloc(table_size*sizeof(int));
	table_tmp.run_length = malloc(table_size*sizeof(int));
	table_tmp.max_bits = malloc((entropy_max_AC_bits + 2)*sizeof(int));
	table_tmp.valoffset = malloc((entropy_max_AC_bits + 2)*sizeof(int));

	// initialize AC table
	first_dimension_bins = 20;
	second_dimension_bins = 20;

	int c,i,j,k;
	if (private_option == 1) {
		ac_table = malloc(3*sizeof(symbol_table_c ***));
		for (c=0; c<3; ++c)
			default_table[c] = FALSE;
		for (c=0; c<3; ++c) {
			ac_table[c] = malloc(64*sizeof(symbol_table_c **));
			for (i=1; i<64; ++i) {
				ac_table[c][i] = malloc((first_dimension_bins + 1)*sizeof(symbol_table_c*));
				for (j=0; j<(first_dimension_bins + 1); ++j) {
					ac_table[c][i][j] = malloc((second_dimension_bins + 5 + 1)*sizeof(symbol_table_c));
					for (k=0; k<second_dimension_bins + 5 + 1; ++k)
						if (!initialize_AC_table(c, i, j, k, private_option)) break;
				}
			}
		}

		dc_table = malloc(3*sizeof(symbol_table_c *));
		for (c=0; c<3; ++c) {
			dc_table[c] = malloc(36*sizeof(symbol_table_c));
			for (i=0; i<36; ++i)
				initialize_DC_table(c, i, private_option);
		}
	} else {
		ac_table_d = malloc(3*sizeof(symbol_table_d ***));
		for (c=0; c<3; ++c)
			default_table[c] = FALSE;
		for (c=0; c<3; ++c) {
			ac_table_d[c] = malloc(64*sizeof(symbol_table_d **));
			for (i=1; i<64; ++i) {
				ac_table_d[c][i] = malloc((first_dimension_bins + 1)*sizeof(symbol_table_d*));
				for (j=0; j<(first_dimension_bins + 1); ++j) {
					ac_table_d[c][i][j] = malloc((second_dimension_bins + 5 + 1)*sizeof(symbol_table_d));
					for (k=0; k<second_dimension_bins + 5 + 1; ++k)
						if (!initialize_AC_table(c, i, j, k, private_option)) break;
				}
			}
		}

		dc_table_d = malloc(3*sizeof(symbol_table_d *));
		for (c=0; c<3; ++c) {
			dc_table_d[c] = malloc(36*sizeof(symbol_table_d));
			for (i=0; i<36; ++i)
				initialize_DC_table(c, i, private_option);
		}

	}

	// initialize max_pos_value
	for (c=0; c<3; ++c) {
		initialize_max_pos_value(c);
	}
	// initialize coef_bins and coef_bins_p
	for (c=0; c<3; ++c) {
		initialize_coef_bins(c);
		initialize_coef_bins_p(c);
	}

	bits_saving = malloc(20*sizeof(int));
	for (i=0; i<20; ++i)
		bits_saving[i] = 0;

	encode_bits = 0;
	decode_bits = 0;
	lossy_saving = 0;
}

/*
 * Expanded entropy decoder object for Huffman decoding.
 *
 * The savable_state subrecord contains fields that change within an MCU,
 * but must not be updated permanently until we complete the MCU.
 */

typedef struct {
  int last_dc_val[MAX_COMPS_IN_SCAN]; /* last DC coef for each component */
  //int last_dc_diff[MAX_COMPS_IN_SCAN]; // - Xing
  previous_block_state_t previous_block_state; // Xing
} savable_state;

/* This macro is to work around compilers with missing or broken
 * structure assignment.  You'll need to fix this code if you have
 * such a compiler and you change MAX_COMPS_IN_SCAN.
 */

#ifndef NO_STRUCT_ASSIGN
#define ASSIGN_STATE(dest,src)  ((dest) = (src))
#else
#if MAX_COMPS_IN_SCAN == 4
#define ASSIGN_STATE(dest,src)  \
        ((dest).last_dc_val[0] = (src).last_dc_val[0], \
         (dest).last_dc_val[1] = (src).last_dc_val[1], \
         (dest).last_dc_val[2] = (src).last_dc_val[2], \
    	 (dest).last_dc_val[3] = (src).last_dc_val[3], \
    	 (dest).last_dc_diff[0] = (src).last_dc_diff[0], \
    	 (dest).last_dc_diff[1] = (src).last_dc_diff[1], \
    	 (dest).last_dc_diff[2] = (src).last_dc_diff[2], \
       (dest).last_dc_diff[3] = (src).last_dc_diff[3], \
       memcpy(&(dest), &(src), sizeof(previous_block_state_t)))
#endif
#endif


typedef struct {
  struct jpeg_entropy_decoder pub; /* public fields */

  /* These fields are loaded into local variables at start of each MCU.
   * In case of suspension, we exit WITHOUT updating them.
   */
  bitread_perm_state bitstate;  /* Bit buffer at start of MCU */
  savable_state saved;          /* Other state at start of MCU */

  /* These fields are NOT loaded into local working state. */
  unsigned int restarts_to_go;  /* MCUs left in this restart interval */

  /* Pointers to derived tables (these workspaces have image lifespan) */
  d_derived_tbl * dc_derived_tbls[NUM_HUFF_TBLS];
  d_derived_tbl * ac_derived_tbls[NUM_HUFF_TBLS];

  /* Precalculated info set up by start_pass for use in decode_mcu: */

  /* Pointers to derived tables to be used for each block within an MCU */
  d_derived_tbl * dc_cur_tbls[D_MAX_BLOCKS_IN_MCU];
  d_derived_tbl * ac_cur_tbls[D_MAX_BLOCKS_IN_MCU];
  /* Whether we care about the DC and AC coefficient values for each block */
  boolean dc_needed[D_MAX_BLOCKS_IN_MCU];
  boolean ac_needed[D_MAX_BLOCKS_IN_MCU];
} huff_entropy_decoder;

typedef huff_entropy_decoder * huff_entropy_ptr;


/*
 * Initialize for a Huffman-compressed scan.
 */

METHODDEF(void)
start_pass_huff_decoder (j_decompress_ptr cinfo)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  int ci, blkn, dctbl, actbl;
  jpeg_component_info * compptr;

  /* Check that the scan parameters Ss, Se, Ah/Al are OK for sequential JPEG.
   * This ought to be an error condition, but we make it a warning because
   * there are some baseline files out there with all zeroes in these bytes.
   */
  if (cinfo->Ss != 0 || cinfo->Se != DCTSIZE2-1 ||
      cinfo->Ah != 0 || cinfo->Al != 0)
    WARNMS(cinfo, JWRN_NOT_SEQUENTIAL);

  int temp1, temp;
  for (ci = 0; ci < cinfo->comps_in_scan; ci++) {
    compptr = cinfo->cur_comp_info[ci];
    dctbl = compptr->dc_tbl_no;
    actbl = compptr->ac_tbl_no;
    /* Compute derived values for Huffman tables */
    /* We may do this more than once for a table, but it's not expensive */
    jpeg_make_d_derived_tbl(cinfo, TRUE, dctbl,
                            & entropy->dc_derived_tbls[dctbl]);
    jpeg_make_d_derived_tbl(cinfo, FALSE, actbl,
                            & entropy->ac_derived_tbls[actbl]);
    /* Initialize DC predictions to 0 */
    entropy->saved.last_dc_val[ci] = 0;
    //entropy->saved.last_dc_diff[ci] = 0; // Xing
	entropy->saved.previous_block_state.current_index[ci] = 0;
	for (temp1=0; temp1<LOOK_BACKWARD_BLOCK; ++temp1)
		entropy->saved.previous_block_state.previous_blocks[ci][temp1] = 0;
		for (temp=0; temp<64; ++temp) {
			//entropy->saved.previous_block_state.previous_blocks[ci][temp1][temp] = -1;
			entropy->saved.previous_block_state.previous_blocks_avgs[ci][temp1][temp] = 0;
		}
  }

  /* Precalculate decoding info for each block in an MCU of this scan */
  for (blkn = 0; blkn < cinfo->blocks_in_MCU; blkn++) {
    ci = cinfo->MCU_membership[blkn];
    compptr = cinfo->cur_comp_info[ci];
    /* Precalculate which table to use for each block */
    entropy->dc_cur_tbls[blkn] = entropy->dc_derived_tbls[compptr->dc_tbl_no];
    entropy->ac_cur_tbls[blkn] = entropy->ac_derived_tbls[compptr->ac_tbl_no];
    /* Decide whether we really care about the coefficient values */
    if (compptr->component_needed) {
      entropy->dc_needed[blkn] = TRUE;
      /* we don't need the ACs if producing a 1/8th-size image */
      entropy->ac_needed[blkn] = (compptr->_DCT_scaled_size > 1);
    } else {
      entropy->dc_needed[blkn] = entropy->ac_needed[blkn] = FALSE;
    }
  }

  /* Initialize bitread state variables */
  entropy->bitstate.bits_left = 0;
  entropy->bitstate.get_buffer = 0; /* unnecessary, but keeps Purify quiet */
  entropy->pub.insufficient_data = FALSE;

  /* Initialize restart counter */
  entropy->restarts_to_go = cinfo->restart_interval;
}


/*
 * Compute the derived values for a Huffman table.
 * This routine also performs some validation checks on the table.
 *
 * Note this is also used by jdphuff.c.
 */

GLOBAL(void)
jpeg_make_d_derived_tbl (j_decompress_ptr cinfo, boolean isDC, int tblno,
                         d_derived_tbl ** pdtbl)
{
  JHUFF_TBL *htbl;
  d_derived_tbl *dtbl;
  int p, i, l, si, numsymbols;
  int lookbits, ctr;
  char huffsize[257];
  unsigned int huffcode[257];
  unsigned int code;

  /* Note that huffsize[] and huffcode[] are filled in code-length order,
   * paralleling the order of the symbols themselves in htbl->huffval[].
   */

  /* Find the input Huffman table */
  if (tblno < 0 || tblno >= NUM_HUFF_TBLS)
    ERREXIT1(cinfo, JERR_NO_HUFF_TABLE, tblno);
  htbl =
    isDC ? cinfo->dc_huff_tbl_ptrs[tblno] : cinfo->ac_huff_tbl_ptrs[tblno];
  if (htbl == NULL)
    ERREXIT1(cinfo, JERR_NO_HUFF_TABLE, tblno);

  /* Allocate a workspace if we haven't already done so. */
  if (*pdtbl == NULL)
    *pdtbl = (d_derived_tbl *)
      (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_IMAGE,
                                  sizeof(d_derived_tbl));
  dtbl = *pdtbl;
  dtbl->pub = htbl;             /* fill in back link */

  /* Figure C.1: make table of Huffman code length for each symbol */

  p = 0;
  for (l = 1; l <= 16; l++) {
    i = (int) htbl->bits[l];
    if (i < 0 || p + i > 256)   /* protect against table overrun */
      ERREXIT(cinfo, JERR_BAD_HUFF_TABLE);
    while (i--)
      huffsize[p++] = (char) l;
  }
  huffsize[p] = 0;
  numsymbols = p;

  /* Figure C.2: generate the codes themselves */
  /* We also validate that the counts represent a legal Huffman code tree. */

  code = 0;
  si = huffsize[0];
  p = 0;
  while (huffsize[p]) {
    while (((int) huffsize[p]) == si) {
      huffcode[p++] = code;
      code++;
    }
    /* code is now 1 more than the last code used for codelength si; but
     * it must still fit in si bits, since no code is allowed to be all ones.
     */
    if (((INT32) code) >= (((INT32) 1) << si))
      ERREXIT(cinfo, JERR_BAD_HUFF_TABLE);
    code <<= 1;
    si++;
  }

  /* Figure F.15: generate decoding tables for bit-sequential decoding */

  p = 0;
  for (l = 1; l <= 16; l++) {
    if (htbl->bits[l]) {
      /* valoffset[l] = huffval[] index of 1st symbol of code length l,
       * minus the minimum code of length l
       */
      dtbl->valoffset[l] = (INT32) p - (INT32) huffcode[p];
      p += htbl->bits[l];
      dtbl->maxcode[l] = huffcode[p-1]; /* maximum code of length l */
    } else {
      dtbl->maxcode[l] = -1;    /* -1 if no codes of this length */
    }
  }
  dtbl->valoffset[17] = 0;
  dtbl->maxcode[17] = 0xFFFFFL; /* ensures jpeg_huff_decode terminates */

  /* Compute lookahead tables to speed up decoding.
   * First we set all the table entries to 0, indicating "too long";
   * then we iterate through the Huffman codes that are short enough and
   * fill in all the entries that correspond to bit sequences starting
   * with that code.
   */

   for (i = 0; i < (1 << HUFF_LOOKAHEAD); i++)
     dtbl->lookup[i] = (HUFF_LOOKAHEAD + 1) << HUFF_LOOKAHEAD;

  p = 0;
  for (l = 1; l <= HUFF_LOOKAHEAD; l++) {
    for (i = 1; i <= (int) htbl->bits[l]; i++, p++) {
      /* l = current code's length, p = its index in huffcode[] & huffval[]. */
      /* Generate left-justified code followed by all possible bit sequences */
      lookbits = huffcode[p] << (HUFF_LOOKAHEAD-l);
      for (ctr = 1 << (HUFF_LOOKAHEAD-l); ctr > 0; ctr--) {
        dtbl->lookup[lookbits] = (l << HUFF_LOOKAHEAD) | htbl->huffval[p];
        lookbits++;
      }
    }
  }

  /* Validate symbols as being reasonable.
   * For AC tables, we make no check, but accept all byte values 0..255.
   * For DC tables, we require the symbols to be in range 0..15.
   * (Tighter bounds could be applied depending on the data depth and mode,
   * but this is sufficient to ensure safe decoding.)
   */
  if (isDC) {
    for (i = 0; i < numsymbols; i++) {
      int sym = htbl->huffval[i];
      if (sym < 0 || sym > 15)
        ERREXIT(cinfo, JERR_BAD_HUFF_TABLE);
    }
  }
}


/*
 * Out-of-line code for bit fetching (shared with jdphuff.c).
 * See jdhuff.h for info about usage.
 * Note: current values of get_buffer and bits_left are passed as parameters,
 * but are returned in the corresponding fields of the state struct.
 *
 * On most machines MIN_GET_BITS should be 25 to allow the full 32-bit width
 * of get_buffer to be used.  (On machines with wider words, an even larger
 * buffer could be used.)  However, on some machines 32-bit shifts are
 * quite slow and take time proportional to the number of places shifted.
 * (This is true with most PC compilers, for instance.)  In this case it may
 * be a win to set MIN_GET_BITS to the minimum value of 15.  This reduces the
 * average shift distance at the cost of more calls to jpeg_fill_bit_buffer.
 */

#ifdef SLOW_SHIFT_32
#define MIN_GET_BITS  15        /* minimum allowable value */
#else
#define MIN_GET_BITS  (BIT_BUF_SIZE-7)
#endif


GLOBAL(boolean)
jpeg_fill_bit_buffer (bitread_working_state * state,
                      register bit_buf_type get_buffer, register int bits_left,
                      int nbits)
/* Load up the bit buffer to a depth of at least nbits */
{
  /* Copy heavily used state fields into locals (hopefully registers) */
  register const JOCTET * next_input_byte = state->next_input_byte;
  register size_t bytes_in_buffer = state->bytes_in_buffer;
  j_decompress_ptr cinfo = state->cinfo;

  /* Attempt to load at least MIN_GET_BITS bits into get_buffer. */
  /* (It is assumed that no request will be for more than that many bits.) */
  /* We fail to do so only if we hit a marker or are forced to suspend. */

  if (cinfo->unread_marker == 0) {      /* cannot advance past a marker */
    while (bits_left < MIN_GET_BITS) {
      register int c;

      /* Attempt to read a byte */
      if (bytes_in_buffer == 0) {
        if (! (*cinfo->src->fill_input_buffer) (cinfo))
          return FALSE;
        next_input_byte = cinfo->src->next_input_byte;
        bytes_in_buffer = cinfo->src->bytes_in_buffer;
      }
      bytes_in_buffer--;
      c = GETJOCTET(*next_input_byte++);

      /* If it's 0xFF, check and discard stuffed zero byte */
      if (c == 0xFF) {
        /* Loop here to discard any padding FF's on terminating marker,
         * so that we can save a valid unread_marker value.  NOTE: we will
         * accept multiple FF's followed by a 0 as meaning a single FF data
         * byte.  This data pattern is not valid according to the standard.
         */
        do {
          if (bytes_in_buffer == 0) {
            if (! (*cinfo->src->fill_input_buffer) (cinfo))
              return FALSE;
            next_input_byte = cinfo->src->next_input_byte;
            bytes_in_buffer = cinfo->src->bytes_in_buffer;
          }
          bytes_in_buffer--;
          c = GETJOCTET(*next_input_byte++);
        } while (c == 0xFF);

        if (c == 0) {
          /* Found FF/00, which represents an FF data byte */
          c = 0xFF;
        } else {
          /* Oops, it's actually a marker indicating end of compressed data.
           * Save the marker code for later use.
           * Fine point: it might appear that we should save the marker into
           * bitread working state, not straight into permanent state.  But
           * once we have hit a marker, we cannot need to suspend within the
           * current MCU, because we will read no more bytes from the data
           * source.  So it is OK to update permanent state right away.
           */
          cinfo->unread_marker = c;
          /* See if we need to insert some fake zero bits. */
          goto no_more_bytes;
        }
      }

      /* OK, load c into get_buffer */
      get_buffer = (get_buffer << 8) | c;
      bits_left += 8;
    } /* end while */
  } else {
  no_more_bytes:
    /* We get here if we've read the marker that terminates the compressed
     * data segment.  There should be enough bits in the buffer register
     * to satisfy the request; if so, no problem.
     */
    if (nbits > bits_left) {
      /* Uh-oh.  Report corrupted data to user and stuff zeroes into
       * the data stream, so that we can produce some kind of image.
       * We use a nonvolatile flag to ensure that only one warning message
       * appears per data segment.
       */
      if (! cinfo->entropy->insufficient_data) {
        WARNMS(cinfo, JWRN_HIT_MARKER);
        cinfo->entropy->insufficient_data = TRUE;
      }
      /* Fill the buffer with zero bits */
      get_buffer <<= MIN_GET_BITS - bits_left;
      bits_left = MIN_GET_BITS;
    }
  }

  /* Unload the local registers */
  state->next_input_byte = next_input_byte;
  state->bytes_in_buffer = bytes_in_buffer;
  state->get_buffer = get_buffer;
  state->bits_left = bits_left;

  return TRUE;
}


/* Macro version of the above, which performs much better but does not
   handle markers.  We have to hand off any blocks with markers to the
   slower routines. */

#define GET_BYTE \
{ \
  register int c0, c1; \
  c0 = GETJOCTET(*buffer++); \
  c1 = GETJOCTET(*buffer); \
  /* Pre-execute most common case */ \
  get_buffer = (get_buffer << 8) | c0; \
  bits_left += 8; \
  if (c0 == 0xFF) { \
    /* Pre-execute case of FF/00, which represents an FF data byte */ \
    buffer++; \
    if (c1 != 0) { \
      /* Oops, it's actually a marker indicating end of compressed data. */ \
      cinfo->unread_marker = c1; \
      /* Back out pre-execution and fill the buffer with zero bits */ \
      buffer -= 2; \
      get_buffer &= ~0xFF; \
    } \
  } \
}

#if __WORDSIZE == 64 || defined(_WIN64)

/* Pre-fetch 48 bytes, because the holding register is 64-bit */
#define FILL_BIT_BUFFER_FAST \
  if (bits_left < 16) { \
    GET_BYTE GET_BYTE GET_BYTE GET_BYTE GET_BYTE GET_BYTE \
  }

#else

/* Pre-fetch 16 bytes, because the holding register is 32-bit */
#define FILL_BIT_BUFFER_FAST \
  if (bits_left < 16) { \
    GET_BYTE GET_BYTE \
  }

#endif


/*
 * Out-of-line code for Huffman code decoding.
 * See jdhuff.h for info about usage.
 */

GLOBAL(int)
jpeg_huff_decode (bitread_working_state * state,
                  register bit_buf_type get_buffer, register int bits_left,
                  d_derived_tbl * htbl, int min_bits)
{
  register int l = min_bits;
  register INT32 code;

  /* HUFF_DECODE has determined that the code is at least min_bits */
  /* bits long, so fetch that many bits in one swoop. */

  CHECK_BIT_BUFFER(*state, l, return -1);
  code = GET_BITS(l);

  /* Collect the rest of the Huffman code one bit at a time. */
  /* This is per Figure F.16 in the JPEG spec. */

  while (code > htbl->maxcode[l]) {
    code <<= 1;
    CHECK_BIT_BUFFER(*state, 1, return -1);
    code |= GET_BITS(1);
    l++;
  }

  /* Unload the local registers */
  state->get_buffer = get_buffer;
  state->bits_left = bits_left;

  /* With garbage input we may reach the sentinel value l = 17. */

  if (l > 16) {
    WARNMS(state->cinfo, JWRN_HUFF_BAD_CODE);
    return 0;                   /* fake a zero as the safest result */
  }

  return htbl->pub->huffval[ (int) (code + htbl->valoffset[l]) ];
}


GLOBAL(int)
jpeg_huff_decode_entropy (bitread_working_state * state,
                  register bit_buf_type get_buffer, register int bits_left,
                  symbol_table_d * htbl, int min_bits)
{
  register int l = min_bits;
  register INT32 code;

  /* HUFF_DECODE has determined that the code is at least min_bits */
  /* bits long, so fetch that many bits in one swoop. */

  CHECK_BIT_BUFFER(*state, l, return -1);
  code = GET_BITS(l);

  /* Collect the rest of the Huffman code one bit at a time. */
  /* This is per Figure F.16 in the JPEG spec. */

  while (code > htbl->max_bits[l]) {
    code <<= 1;
    CHECK_BIT_BUFFER(*state, 1, return -1);
    code |= GET_BITS(1);
    l++;
  }

  /* Unload the local registers */
  state->get_buffer = get_buffer;
  state->bits_left = bits_left;

  /* With garbage input we may reach the sentinel value l = 17. */

  if (l > 16) {
    WARNMS(state->cinfo, JWRN_HUFF_BAD_CODE);
    return 0;                   /* fake a zero as the safest result */
  }

  return htbl->run_length[ (int) (code + htbl->valoffset[l]) ];
}


/*
 * Figure F.12: extend sign bit.
 * On some machines, a shift and add will be faster than a table lookup.
 */

#define AVOID_TABLES
#ifdef AVOID_TABLES

#define HUFF_EXTEND(x,s)  ((x) + ((((x) - (1<<((s)-1))) >> 31) & (((-1)<<(s)) + 1)))

#else

#define HUFF_EXTEND(x,s)  ((x) < extend_test[s] ? (x) + extend_offset[s] : (x))

static const int extend_test[16] =   /* entry n is 2**(n-1) */
  { 0, 0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0040, 0x0080,
    0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x2000, 0x4000 };

static const int extend_offset[16] = /* entry n is (-1 << n) + 1 */
  { 0, ((-1)<<1) + 1, ((-1)<<2) + 1, ((-1)<<3) + 1, ((-1)<<4) + 1,
    ((-1)<<5) + 1, ((-1)<<6) + 1, ((-1)<<7) + 1, ((-1)<<8) + 1,
    ((-1)<<9) + 1, ((-1)<<10) + 1, ((-1)<<11) + 1, ((-1)<<12) + 1,
    ((-1)<<13) + 1, ((-1)<<14) + 1, ((-1)<<15) + 1 };

#endif /* AVOID_TABLES */


/*
 * Check for a restart marker & resynchronize decoder.
 * Returns FALSE if must suspend.
 */

LOCAL(boolean)
process_restart (j_decompress_ptr cinfo)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  int ci;

  /* Throw away any unused bits remaining in bit buffer; */
  /* include any full bytes in next_marker's count of discarded bytes */
  cinfo->marker->discarded_bytes += entropy->bitstate.bits_left / 8;
  entropy->bitstate.bits_left = 0;

  /* Advance past the RSTn marker */
  if (! (*cinfo->marker->read_restart_marker) (cinfo))
    return FALSE;

  /* Re-initialize DC predictions to 0 */
  int temp1, temp;
  for (ci = 0; ci < cinfo->comps_in_scan; ci++) {
    entropy->saved.last_dc_val[ci] = 0;
    //entropy->saved.last_dc_diff[ci] = 0; // Xing
  	entropy->saved.previous_block_state.current_index[ci] = 0;
  	//memset(&entropy->saved.previous_block_state.previous_blocks_avgs[0][0][0], 0, ci*LOOK_BACKWARD_BLOCK*64);

  	for (temp1=0; temp1<LOOK_BACKWARD_BLOCK; ++temp1)
  		entropy->saved.previous_block_state.previous_blocks[ci][temp1] = 0;
  		for (temp=0; temp<64; ++temp) {
  			//entropy->saved.previous_block_state.previous_blocks[ci][temp1][temp] = -1;
  			entropy->saved.previous_block_state.previous_blocks_avgs[ci][temp1][temp] = 0;
  			//entropy->saved.previous_block_state.previous_blocks[ci][temp1][temp] = 0;
  		}

  }

  /* Reset restart counter */
  entropy->restarts_to_go = cinfo->restart_interval;

  /* Reset out-of-data flag, unless read_restart_marker left us smack up
   * against a marker.  In that case we will end up treating the next data
   * segment as empty, and we can avoid producing bogus output pixels by
   * leaving the flag set.
   */
  if (cinfo->unread_marker == 0)
    entropy->pub.insufficient_data = FALSE;

  return TRUE;
}


LOCAL(boolean)
decode_mcu_slow (j_decompress_ptr cinfo, JBLOCKROW *MCU_data)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  BITREAD_STATE_VARS;
  int blkn;
  savable_state state;
  /* Outer loop handles each block in the MCU */

  /* Load up working state */
  BITREAD_LOAD_STATE(cinfo,entropy->bitstate);
  ASSIGN_STATE(state, entropy->saved);

  for (blkn = 0; blkn < cinfo->blocks_in_MCU; blkn++) {
    JBLOCKROW block = MCU_data[blkn];
    d_derived_tbl * dctbl = entropy->dc_cur_tbls[blkn];
    d_derived_tbl * actbl = entropy->ac_cur_tbls[blkn];
    register int s, k, r;

    /* Decode a single block's worth of coefficients */

    /* Section F.2.2.1: decode the DC coefficient difference */
    HUFF_DECODE(s, br_state, dctbl, return FALSE, label1);
    if (s) {
      CHECK_BIT_BUFFER(br_state, s, return FALSE);
      r = GET_BITS(s);
      s = HUFF_EXTEND(r, s);
    }

    if (entropy->dc_needed[blkn]) {
      /* Convert DC difference to actual value, update last_dc_val */
      int ci = cinfo->MCU_membership[blkn];
      s += state.last_dc_val[ci];
      state.last_dc_val[ci] = s;
      /* Output the DC coefficient (assumes jpeg_natural_order[0] = 0) */
      (*block)[0] = (JCOEF) s;
    }

    if (entropy->ac_needed[blkn]) {

      /* Section F.2.2.2: decode the AC coefficients */
      /* Since zeroes are skipped, output area must be cleared beforehand */
      for (k = 1; k < DCTSIZE2; k++) {
        HUFF_DECODE(s, br_state, actbl, return FALSE, label2);

        r = s >> 4;
        s &= 15;

        if (s) {
          k += r;
          CHECK_BIT_BUFFER(br_state, s, return FALSE);
          r = GET_BITS(s);
          s = HUFF_EXTEND(r, s);
          /* Output coefficient in natural (dezigzagged) order.
           * Note: the extra entries in jpeg_natural_order[] will save us
           * if k >= DCTSIZE2, which could happen if the data is corrupted.
           */
          (*block)[jpeg_natural_order[k]] = (JCOEF) s;
        } else {
          if (r != 15)
            break;
          k += 15;
        }
      }

    } else {

      /* Section F.2.2.2: decode the AC coefficients */
      /* In this path we just discard the values */
      for (k = 1; k < DCTSIZE2; k++) {
        HUFF_DECODE(s, br_state, actbl, return FALSE, label3);

        r = s >> 4;
        s &= 15;

        if (s) {
          k += r;
          CHECK_BIT_BUFFER(br_state, s, return FALSE);
          DROP_BITS(s);
        } else {
          if (r != 15)
            break;
          k += 15;
        }
      }
    }
  }

  /* Completed MCU, so update state */
  BITREAD_SAVE_STATE(cinfo,entropy->bitstate);
  ASSIGN_STATE(entropy->saved, state);
  return TRUE;
}


LOCAL(boolean)
decode_mcu_slow_entropy (j_decompress_ptr cinfo, JBLOCKROW *MCU_data)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  BITREAD_STATE_VARS;
  int blkn;
  savable_state state;
  /* Outer loop handles each block in the MCU */

  /* Load up working state */
  BITREAD_LOAD_STATE(cinfo,entropy->bitstate);
  ASSIGN_STATE(state, entropy->saved);

  int ci, tmp, tmp2;
  register int s, k, r, t;
  register symbol_table_d* p_table;
  JBLOCKROW block;
  previous_block_state_t * pre_state = &state.previous_block_state;
  UINT8 *previous_blocks_avgs, *previous_blocks_avgs_ma;
  JCOEF * previous_blocks;
  int index0, index1, index2, index3;
  for (blkn = 0; blkn < cinfo->blocks_in_MCU; blkn++) {
    block = MCU_data[blkn];
    t = 0;
    ci = cinfo->MCU_membership[blkn];
    index0 = pre_state->current_index[ci];
      index1 = index0 == 0 ? LOOK_BACKWARD_BLOCK : index0 - 1;
      index2 = index1 == 0 ? LOOK_BACKWARD_BLOCK : index1 - 1;
      index3 = index2 == 0 ? LOOK_BACKWARD_BLOCK : index2 - 1;

    previous_blocks_avgs = pre_state->previous_blocks_avgs[ci][index0];
    previous_blocks_avgs_ma = pre_state->previous_blocks_avgs_ma[ci][index0];
    previous_blocks = &pre_state->previous_blocks[ci][index0];
    memset(previous_blocks_avgs, 0, 64*sizeof(UINT8));

    p_table = (symbol_table_d *)&dc_table_d[ci][get_dc_index(ci, pre_state, index1, index2)];

    /* Decode a single block's worth of coefficients */

    /* Section F.2.2.1: decode the DC coefficient difference */
    HUFF_DECODE_ENTROPY(s, br_state, p_table, return FALSE, label1);
    r = tmp = s - 11;
    tmp2 = tmp >> (CHAR_BIT * sizeof(int) - 1);
    tmp ^= tmp2;
    tmp -= tmp2;
    if (r) {
      tmp2 = tmp - 1;
      if (tmp2)
      {
    	  CHECK_BIT_BUFFER(br_state, tmp2, return FALSE);
    	  s = GET_BITS(tmp2) | (1<<tmp2);
      }
      else s = 1;
      if (r < 0) s=-s;
    } else s=0;

    // for better dc
    *previous_blocks = r;
    // for better dc

      /* Convert DC difference to actual value, update last_dc_val */
      s += state.last_dc_val[ci];
      state.last_dc_val[ci] = s;
      /* Output the DC coefficient (assumes jpeg_natural_order[0] = 0) */
      (*block)[0] = (JCOEF) s;


    int real_last_non_zero = 1;
      /* Section F.2.2.2: decode the AC coefficients */
      /* Since zeroes are skipped, output area must be cleared beforehand */

      // handle k=1 separately, to avoid "if" in get_first_dimension_index


      for (k = 1; k < DCTSIZE2; k++) {
    	  p_table = (symbol_table_d *)&ac_table_d[ci][k][get_first_dimension_index(ci, k, t*1000/max_pos_value_range[ci][1][k], tmp)][get_second_dimension_index(ci, k, &state.previous_block_state, index1, index2, index3)];
    	  HUFF_DECODE_ENTROPY(s, br_state, p_table, return FALSE, label2);

        r = s >> 4;
        s &= 15;

        if (s) {
            tmp = reverse_jpeg_nbits_table[s];
            t += tmp;
          k += r;
          if (tmp<=3) {
        	  CHECK_BIT_BUFFER(br_state, 1, return FALSE);
               	  r = GET_BITS(1);
             	  if (r) s = (INT32) entry_to_number_table[s];
                  else s = (INT32) (-entry_to_number_table[s]);
          } else {
                	 CHECK_BIT_BUFFER(br_state, tmp, return FALSE);
                	 r = GET_BITS(tmp);
                	 s = HUFF_EXTEND(r, tmp);
          }
          /* Output coefficient in natural (dezigzagged) order.
           * Note: the extra entries in jpeg_natural_order[] will save us
           * if k >= DCTSIZE2, which could happen if the data is corrupted.
           */
          (*block)[jpeg_natural_order[k]] = (JCOEF) s;
		  r = k - LOOK_FORWARD_COEF + 1;
		if (r < real_last_non_zero)
		  r = real_last_non_zero;
		memset(&previous_blocks_avgs[r], tmp, k-r+1);
		memcpy(&previous_blocks_avgs_ma[r], &max_pos_value_range_r[ci][k][r], k-r+1);
		/* fast record status for dimension-2 value */
		real_last_non_zero = k + 1;
        } else {
          if (r != 15)
            break;
          k += 15;
        }
      }

    /*now_index = pre_state->current_index[ci];
    memcpy(pre_state->previous_blocks[ci][now_index],
            pre_state->previous_blocks[ci][LOOK_BACKWARD_BLOCK],
               64*sizeof(JCOEF));
    memcpy(pre_state->previous_blocks_avgs[ci][now_index],
    		pre_state->previous_blocks_avgs[ci][LOOK_BACKWARD_BLOCK],
        		   64*sizeof(UINT8));
    memcpy(pre_state->previous_blocks_avgs_ma[ci][now_index],
    		pre_state->previous_blocks_avgs_ma[ci][LOOK_BACKWARD_BLOCK],
        		   64*sizeof(UINT8));
    memset(pre_state->previous_blocks_avgs[ci][LOOK_BACKWARD_BLOCK], 0, 64*sizeof(UINT8));   // not sure if this is 100% correct, check later, basically mark every INT to -1
    */
    //for (int temp=1; temp<64; ++temp) {
    //	state.previous_block_state.previous_blocks_avgs[ci][now_index][temp] = -1;
    //}
    pre_state->current_index[ci] = index3;
  }

  /* Completed MCU, so update state */
  BITREAD_SAVE_STATE(cinfo,entropy->bitstate);
  ASSIGN_STATE(entropy->saved, state);
  return TRUE;
}


LOCAL(boolean)
decode_mcu_fast (j_decompress_ptr cinfo, JBLOCKROW *MCU_data)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  BITREAD_STATE_VARS;
  JOCTET *buffer;
  int blkn;
  savable_state state;
  /* Outer loop handles each block in the MCU */

  /* Load up working state */
  BITREAD_LOAD_STATE(cinfo,entropy->bitstate);
  buffer = (JOCTET *) br_state.next_input_byte;
  ASSIGN_STATE(state, entropy->saved);

  for (blkn = 0; blkn < cinfo->blocks_in_MCU; blkn++) {
    JBLOCKROW block = MCU_data[blkn];
    d_derived_tbl * dctbl = entropy->dc_cur_tbls[blkn];
    d_derived_tbl * actbl = entropy->ac_cur_tbls[blkn];
    register int s, k, r, l;

    HUFF_DECODE_FAST(s, l, dctbl);
    if (s) {
      FILL_BIT_BUFFER_FAST
      r = GET_BITS(s);
      s = HUFF_EXTEND(r, s);
    }

    if (entropy->dc_needed[blkn]) {
      int ci = cinfo->MCU_membership[blkn];
      s += state.last_dc_val[ci];
      state.last_dc_val[ci] = s;
      (*block)[0] = (JCOEF) s;
    }

    if (entropy->ac_needed[blkn]) {

      for (k = 1; k < DCTSIZE2; k++) {
        HUFF_DECODE_FAST(s, l, actbl);
        r = s >> 4;
        s &= 15;

        if (s) {
          k += r;
          FILL_BIT_BUFFER_FAST
          r = GET_BITS(s);
          s = HUFF_EXTEND(r, s);
          (*block)[jpeg_natural_order[k]] = (JCOEF) s;
        } else {
          if (r != 15) break;
          k += 15;
        }
      }

    } else {

      for (k = 1; k < DCTSIZE2; k++) {
        HUFF_DECODE_FAST(s, l, actbl);
        r = s >> 4;
        s &= 15;

        if (s) {
          k += r;
          FILL_BIT_BUFFER_FAST
          DROP_BITS(s);
        } else {
          if (r != 15) break;
          k += 15;
        }
      }
    }
  }

  if (cinfo->unread_marker != 0) {
    cinfo->unread_marker = 0;
    return FALSE;
  }

  br_state.bytes_in_buffer -= (buffer - br_state.next_input_byte);
  br_state.next_input_byte = buffer;
  BITREAD_SAVE_STATE(cinfo,entropy->bitstate);
  ASSIGN_STATE(entropy->saved, state);
  return TRUE;
}



LOCAL(boolean)
decode_mcu_fast_entropy (j_decompress_ptr cinfo, JBLOCKROW *MCU_data)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  BITREAD_STATE_VARS;
  JOCTET *buffer;
  int blkn;
  savable_state state;
  /* Outer loop handles each block in the MCU */

  /* Load up working state */
  BITREAD_LOAD_STATE(cinfo,entropy->bitstate);
  buffer = (JOCTET *) br_state.next_input_byte;
  ASSIGN_STATE(state, entropy->saved);

  int ci, tmp, tmp2;
  register int s, k, r, t, l;
  register symbol_table_d* p_table;
  JBLOCKROW block;
  previous_block_state_t * pre_state = &state.previous_block_state;
  UINT8 *previous_blocks_avgs, *previous_blocks_avgs_ma;
  JCOEF *previous_blocks;

  int index0, index1, index2, index3;
  for (blkn = 0; blkn < cinfo->blocks_in_MCU; blkn++) {
    block = MCU_data[blkn];
    t = 0;
    ci = cinfo->MCU_membership[blkn];
    index0 = pre_state->current_index[ci];
      index1 = index0 == 0 ? LOOK_BACKWARD_BLOCK : index0 - 1;
      index2 = index1 == 0 ? LOOK_BACKWARD_BLOCK : index1 - 1;
      index3 = index2 == 0 ? LOOK_BACKWARD_BLOCK : index2 - 1;

      previous_blocks_avgs = pre_state->previous_blocks_avgs[ci][index0];
      previous_blocks_avgs_ma = pre_state->previous_blocks_avgs_ma[ci][index0];
      previous_blocks = &pre_state->previous_blocks[ci][index0];
      memset(previous_blocks_avgs, 0, 64*sizeof(UINT8));
    p_table = (symbol_table_d *)&dc_table_d[ci][get_dc_index(ci, pre_state, index1, index2)];

    HUFF_DECODE_FAST_ENTROPY(s, l, p_table);

    //state.last_dc_diff[ci] = 0;
    r = tmp = s - 11;
    tmp2 = tmp >> (CHAR_BIT * sizeof(int) - 1);
    tmp ^= tmp2;
    tmp -= tmp2;
    if (r) {
      FILL_BIT_BUFFER_FAST
      tmp2 = tmp - 1;
      if (tmp2)
      {
    	  CHECK_BIT_BUFFER(br_state, tmp2, return FALSE);
    	  s = GET_BITS(tmp2) | (1<<tmp2);
      }
      else s = 1;
      if (r < 0) s=-s;
    } else s=0;


    // for better dc
    *previous_blocks = r;
    // for better dc

      s += state.last_dc_val[ci];
      state.last_dc_val[ci] = s;
      (*block)[0] = (JCOEF) s;

    int real_last_non_zero = 1;
      for (k = 1; k < DCTSIZE2; k++) {
        p_table = (symbol_table_d *)&ac_table_d[ci][k][get_first_dimension_index(ci, k, t*1000/max_pos_value_range[ci][1][k], tmp)][get_second_dimension_index(ci, k, &state.previous_block_state, index1, index2, index3)];
        HUFF_DECODE_FAST_ENTROPY(s, l, p_table);
        r = s >> 4;
        s &= 15;

        if (s) {
          k += r;
          tmp = reverse_jpeg_nbits_table[s];
          t += tmp;

          FILL_BIT_BUFFER_FAST
          if (tmp<=3) {
        	  r = GET_BITS(1);
        	  if (r) s = (INT32) entry_to_number_table[s];
        	  else s = (INT32) (-entry_to_number_table[s]);
          } else {
            r = GET_BITS(tmp);
            s = HUFF_EXTEND(r, tmp);
          }
          (*block)[jpeg_natural_order[k]] = (JCOEF) s;
		  r = k - LOOK_FORWARD_COEF + 1;
		if (r < real_last_non_zero)
		  r = real_last_non_zero;
		memset(&previous_blocks_avgs[r], tmp, k-r+1);
		memcpy(&previous_blocks_avgs_ma[r], &max_pos_value_range_r[ci][k][r], k-r+1);
		/* fast record status for dimension-2 value */
		real_last_non_zero = k + 1;
        } else {
          if (r != 15) break;
          k += 15;
        }
      }

    pre_state->current_index[ci] = index3;
  }

  if (cinfo->unread_marker != 0) {
    cinfo->unread_marker = 0;
    return FALSE;
  }

  br_state.bytes_in_buffer -= (buffer - br_state.next_input_byte);
  br_state.next_input_byte = buffer;
  BITREAD_SAVE_STATE(cinfo,entropy->bitstate);
  ASSIGN_STATE(entropy->saved, state);
  return TRUE;
}



/*
 * Decode and return one MCU's worth of Huffman-compressed coefficients.
 * The coefficients are reordered from zigzag order into natural array order,
 * but are not dequantized.
 *
 * The i'th block of the MCU is stored into the block pointed to by
 * MCU_data[i].  WE ASSUME THIS AREA HAS BEEN ZEROED BY THE CALLER.
 * (Wholesale zeroing is usually a little faster than retail...)
 *
 * Returns FALSE if data source requested suspension.  In that case no
 * changes have been made to permanent state.  (Exception: some output
 * coefficients may already have been assigned.  This is harmless for
 * this module, since we'll just re-assign them on the next call.)
 */

#define BUFSIZE (DCTSIZE2 * 2)

METHODDEF(boolean)
decode_mcu (j_decompress_ptr cinfo, JBLOCKROW *MCU_data)
{
  huff_entropy_ptr entropy = (huff_entropy_ptr) cinfo->entropy;
  int usefast = 1;
  //usefast = 0;

  /* Process restart marker if needed; may have to suspend */
  if (cinfo->restart_interval) {
    if (entropy->restarts_to_go == 0)
      if (! process_restart(cinfo))
        return FALSE;
    usefast = 0;
  }

  if (cinfo->src->bytes_in_buffer < BUFSIZE * (size_t)cinfo->blocks_in_MCU
    || cinfo->unread_marker != 0)
    usefast = 0;

  /* If we've run out of data, just leave the MCU set to zeroes.
   * This way, we return uniform gray for the remainder of the segment.
   */
  if (! entropy->pub.insufficient_data) {
    if (cinfo->private_option == 2) {
		if (usefast) {
		  if (!decode_mcu_fast_entropy(cinfo, MCU_data)) goto use_slow_entropy;
		}
		else {
		  use_slow_entropy:
		  if (!decode_mcu_slow_entropy(cinfo, MCU_data)) return FALSE;
		}
    }
    else {
		if (usefast) {
		  if (!decode_mcu_fast(cinfo, MCU_data)) goto use_slow;
		}
		else {
		  use_slow:
		  if (!decode_mcu_slow(cinfo, MCU_data)) return FALSE;
		}
    }
  }

  /* Account for restart interval (no-op if not using restarts) */
  entropy->restarts_to_go--;

  return TRUE;
}


/*
 * Module initialization routine for Huffman entropy decoding.
 */

GLOBAL(void)
jinit_huff_decoder (j_decompress_ptr cinfo)
{
  huff_entropy_ptr entropy;
  int i;

  /* Motion JPEG frames typically do not include the Huffman tables if they
     are the default tables.  Thus, if the tables are not set by the time
     the Huffman decoder is initialized (usually within the body of
     jpeg_start_decompress()), we set them to default values. */
  std_huff_tables((j_common_ptr) cinfo);

  entropy = (huff_entropy_ptr)
    (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_IMAGE,
                                sizeof(huff_entropy_decoder));
  cinfo->entropy = (struct jpeg_entropy_decoder *) entropy;
  entropy->pub.start_pass = start_pass_huff_decoder;
  entropy->pub.decode_mcu = decode_mcu;

  /* Mark tables unallocated */
  for (i = 0; i < NUM_HUFF_TBLS; i++) {
    entropy->dc_derived_tbls[i] = entropy->ac_derived_tbls[i] = NULL;
  }
}
